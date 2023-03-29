import pandas as pd


class SpatialDataSubmissionFormError(Exception):
    pass


class Report:
    def __init__(self, excel_path, sheet_name="DATASET DETAILS"):
        self.source = excel_path
        self.sheet_name = sheet_name

        self.df = self.to_dataframe(self.sheet_name)
        self.feature_class_name, self.feature_shape, self.feature_type = self.report_details()

    def to_dataframe(self, sheet_name):
        df = pd.read_excel(
            io=self.source,
            sheet_name=sheet_name,
            index_col=0
        )
        df = df.where(pd.notnull(df), None)  # Remove NaN values with None
        df = df[pd.notnull(df.index)]  # Remove blank lines from index
        return df

    def report_details(self):
        df_feature_details = self.df.iloc[0:3, 0:1]  # first col in excel is index - col 0 in df is second col in excel
        df_feature_details = df_feature_details.where(pd.notnull(df_feature_details), None)  # Convert nan to None

        df_feature_details = df_feature_details.T  # Transpose
        df_feature_details.columns = [x.strip(":") for x in df_feature_details.columns]

        feature_class_name = df_feature_details['Feature Class Name'].values[0]
        shape_type = df_feature_details["Shape Type"].values[0] or "Enterprise Geodatabase Table"
        feature_type = df_feature_details["Feature Type"].values[0]

        return [feature_class_name, shape_type, feature_type]


class FieldsReport(Report):
    def __init__(self, excel_path, sheet_name="DATASET DETAILS"):
        super().__init__(excel_path, sheet_name)
        self.field_details = self.field_info()

        if "Subtype Field" in [x for x in self.field_details.columns]:
            self.subtype_fields = self.subtype_info()

    def subtype_info(self):
        fields_df = self.field_details

        if "Subtype Field" not in [x for x in fields_df.columns]:
            return ()

        subtype_field_df = fields_df[fields_df["Subtype Field"].notnull()]

        if not subtype_field_df.empty:
            subtype_fields = (x for x in subtype_field_df["Field Name"])
            return subtype_fields

    def field_info(self):
        df_index_values = self.df.index.values.tolist()

        last_field_name = "GLOBALID"

        if self.feature_type.upper() == "FEATURE CLASS":
            last_field_name = "SHAPE_Length"

            if self.feature_shape.upper() == "POLYGON":
                if "SHAPE_AREA" not in [str(x).upper() for x in df_index_values] or "SHAPE_LENGTH" not in [str(x).upper() for x in df_index_values]:
                    raise IndexError(f"ERROR: SDSF needs to have SHAPE_AREA and SHAPE_LENGTH fields.")

            elif self.feature_shape.upper() == "LINE":
                if "SHAPE_LENGTH" not in [str(x).upper() for x in df_index_values]:
                    raise IndexError(f"ERROR: SDSF needs to have a SHAPE_LENGTH field.")

        df_field_details = self.df.loc["Field Name":last_field_name]

        df_field_details.reset_index(inplace=True)

        df_field_details.columns = df_field_details.iloc[0]  # Set DataFrame columns as first row
        columns = [x for x in df_field_details.columns if x]

        df_field_details = df_field_details.loc[:, columns]  # Limit columns to columns list

        df_field_details = df_field_details.iloc[1:]  # Ignore columns row as a data row

        return df_field_details

    def domain_fields(self) -> dict:
        domain_fields = self.field_details[["Field Name", "Domain", "Field Type"]][
            ~self.field_details["Domain"].isnull()]

        domain_fields_info = domain_fields.to_dict("records")

        return domain_fields_info


class DomainsReport(Report):
    def __init__(self, excel_path, subtype_field=(), sheet_name="DATASET DETAILS"):
        super().__init__(excel_path, sheet_name)

        self.subtype_field = subtype_field

        self.domain_df = pd.DataFrame()

        self.domain_names, self.domain_data = list(), dict()

    def domain_info(self):
        """
        :return: {domain_name, dataframe, subtype_code}
        """

        domain_dataframes = dict()

        # Get domain info from main spreadsheet - Starts at first row after "Common Attribute Values for Fields"
        self.domain_df = self.df.loc["Common Attribute Values for Fields":].iloc[1:]

        # Check index for a mis-named SourceAccuracy field
        df_index = self.domain_df.index.tolist()
        for count, value in enumerate(df_index):
            if type(value) == str and "SourceAccuracy" in value:
                df_index[count] = "SourceAccuracy"

        self.domain_df.index = df_index

        # Create json structure for domains
        index_data = dict()
        subtype_data = dict()

        # Iterate through index to domains
        for count, index_value in enumerate(self.domain_df.index):

            if index_value == "Code":
                domain_name = self.domain_df.index[count - 1]

                row_index_start = self.domain_df.index.tolist().index(domain_name)  # Domain name will precede row index with value of Code

                index_data[domain_name] = {"start_index": row_index_start}

        domain_names = list(index_data.keys())
        last_domain = domain_names[-1]

        for count, current_domain_name in enumerate(domain_names):
            next_domain = None

            if current_domain_name != last_domain:
                next_domain = domain_names[count + 1]

            if next_domain:
                domain_df = self.domain_df.loc[current_domain_name: next_domain]

            else:
                domain_df = self.domain_df.loc[current_domain_name:]

            domain_df.reset_index(inplace=True)  # Adds current index as first column
            domain_df.columns = domain_df.iloc[1]  # Set first column as df header

            domain_name = domain_df.iloc[0, 0]
            domain_field = domain_df.iloc[0, 1]
            subtype_code = domain_df.iloc[0, 2]
            domain_subtype = {"subtype_code": subtype_code, "domain_field": domain_field, "subtype_field": self.subtype_field}  # TODO: include subtype field
            subtype_data[domain_name] = domain_subtype

            if next_domain:
                # domain name, domain field, subtype code
                domain_df = domain_df.iloc[2:-1, :2]  # Only select 2nd to 2nd last row and first two columns

            else:
                domain_df = domain_df.iloc[2:, :2]  # Only select 2nd to 2nd last row and first two columns

            domain_df.dropna(inplace=True)

            # Clean
            # Remove any domain dataframes with empty rows
            num_df_rows = len(domain_df.index)
            if not num_df_rows == 0:
                domain_dataframes[current_domain_name] = domain_df

        return subtype_data, domain_dataframes
