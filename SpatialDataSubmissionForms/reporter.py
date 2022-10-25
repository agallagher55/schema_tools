import pandas as pd


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
        shape_type = df_feature_details["Shape Type"].values[0]
        feature_type = df_feature_details["Feature Type"].values[0]

        return [feature_class_name, shape_type, feature_type]


class FieldsReport(Report):
    def __init__(self, excel_path, sheet_name="DATASET DETAILS"):
        super().__init__(excel_path, sheet_name)
        self.field_details = self.field_info()

    def field_info(self):
        cols = (
            "Field Name", "Description", "Alias", "Field Type",
            "Field Length (# of characters)", "Nullable", "Default Value", "Domain", "Notes"
        )

        df_field_details = self.df.loc["Field Name":"SHAPE_Length"]
        df_field_details.reset_index(inplace=True)

        df_field_details.columns = df_field_details.iloc[0]  # Set DataFrame columns as first row
        df_field_details = df_field_details.loc[:, cols]  # Limit columns to columns list

        df_field_details = df_field_details.iloc[1:]  # Ignore columns row as a data row

        return df_field_details

    def domain_fields(self) -> dict:
        domain_fields = self.field_details[["Field Name", "Domain", "Field Type"]][~self.field_details["Domain"].isnull()]

        domain_fields_info = domain_fields.to_dict("records")

        return domain_fields_info


class DomainsReport(Report):
    def __init__(self, excel_path, sheet_name="DATASET DETAILS"):
        super().__init__(excel_path, sheet_name)

        self.domain_names = list()
        self.domain_data = dict()
        self.domain_df = pd.DataFrame()

        self.domain_info()

    def domain_info(self) -> dict:
        """

        :return:
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
        domain_data = dict()

        # Iterate through index to domains
        for count, index_value in enumerate(self.domain_df.index):

            if index_value == "Code":
                domain_name = self.domain_df.index[count - 1]  # Domain name will precede row index with value of Code
                row_index_start = self.domain_df.index.tolist().index(domain_name)
                domain_data[domain_name] = {"start_index": row_index_start}

        domain_names = list(domain_data.keys())
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

            if next_domain:
                domain_df = domain_df.iloc[2:-1, :2]  # Only select 2nd to 2nd last row and first two columns
            else:
                domain_df = domain_df.iloc[2:, :2]  # Only select 2nd to 2nd last row and first two columns

            domain_df.dropna(inplace=True)

            # Clean
            # Remove any domain dataframes with empty rows
            num_df_rows = len(domain_df.index)
            if not num_df_rows == 0:
                domain_dataframes[current_domain_name] = domain_df

        self.domain_data = domain_dataframes
        self.domain_names = list(self.domain_data.keys())

        return domain_dataframes


if __name__ == "__main__":
    from settings import (
        EXCEL_FILES
    )

    for excel_file in EXCEL_FILES:
        print(f"Processing file: '{excel_file}'")
        # field_data = FieldsReport(excel_file)
        domain_data = DomainsReport(excel_file)
        print(dir(domain_data))
