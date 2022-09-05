import pandas as pd


class SubmissionForm:
    def __init__(self, source, sheet_name):
        """
        :param source: Excel file
        :param sheet_name: Name of Excel sheet containing schema info
        """

        self.source = source
        self.sheet_name = sheet_name

        self.df = self.dataframe()
        self.domains = set(self.df[self.df["Domain"].notnull()]["Domain"].tolist())
        self.sheets = self.sheets()

    def dataframe(self):
        df = pd.read_excel(self.source, sheet_name=self.sheet_name)
        return df

    def sheets(self):
        xl = pd.ExcelFile(self.source)
        sheet_names = xl.sheet_names
        return sheet_names

    def new_domains(self) -> dict:
        """
        :return: {domain_name: domain_DataFrame,...}
        """

        domain_sheets = [sheet for sheet in self.sheets if "DOMAIN" in sheet.upper()]
        dfs = {sheet.replace("Domain ", ""): pd.read_excel(self.source, sheet_name=sheet) for sheet in domain_sheets}
        return dfs


if __name__ == "__main__":
    ped_ramps_xl = r"T:\work\giss\monthly\202209sept\gallaga\Pedestrian Ramps\Pedestrian Ramps Tactiles 10May2022.xlsx"
    sheet = "AST_ped_ramp"

    form = SubmissionForm(ped_ramps_xl, sheet)
    print(form.df)
    print(form.domains)
