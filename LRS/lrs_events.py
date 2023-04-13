import os
import arcpy

import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

class LrsEventForm:

    standard_fields = ("OBJECTID", "FROMDATE", "TODATE", "EVENTID", "ROUTEID", "LOCERROR", "SHAPE")

    def __init__(self, source, sheet_name):
        self.source = source
        self.sheet_name = sheet_name

        self.df = pd.read_excel(source, sheet_name=sheet_name)
        self.df = self.df.fillna('')

        self.event_field = self.get_event_field()

    def get_event_field(self):
        # TODO: Change this to 'get Event Field', and set as instance attribute

        # Add Event-specific field
        # Event field is the first row after LOCERROR
        # Get index of row with LOCERROR
        locerror_idx = self.df["FieldName"].tolist().index("LOCERROR")
        event_field_info = self.df.iloc[locerror_idx + 1]
        return event_field_info.loc["FieldName"]

    def field_info(self):
        self.df.set_index("FieldName", inplace=True)

        fields = [x for x in self.df.index if x not in ("OBJECTID", "GLOBALID", "SHAPE")]
        field_info_df = self.df.loc[fields]

        field_info_df.reset_index(inplace=True)
        self.df.reset_index(inplace=True)

        field_info = field_info_df.to_dict('records')

        # TODO: Translate field types

        return field_info


def add_editor_tracking_fields(feature):
    print(f"\nAdding Editor Tracking fields to '{feature}'...")
    feature_fields = [x.name for x in arcpy.ListFields(feature)]

    field_info = {
        "ADDBY": {
            "field_type": "TEXT",
            "field_length": 32,
            "field_alias": "Add By"
        },
        "MODBY": {
            "field_type": "TEXT",
            "field_length": 32,
            "field_alias": "Modified By"
        },
        "ADDDATE": {
            "field_type": "DATE",
            "field_length": "",
            "field_alias": "Add Date"
        },
        "MODDATE": {
            "field_type": "DATE",
            "field_length": "",
            "field_alias": "Modified Date"
        },
    }

    for field in field_info:
        if field not in feature_fields:
            print(f"\tAdding '{field}' field...")

            field_type = field_info[field]["field_type"]
            field_length = field_info[field]["field_length"]
            field_alias = field_info[field]["field_alias"]

            arcpy.AddField_management(feature, field, field_type, "", "", field_length, field_alias)


if __name__ == "__main__":
    xl = r"T:\work\giss\monthly\202304apr\gallaga\LRS\Activity4_event_design\HRM_Activity4_event_design_28Feb2023.xlsx"

    workbook = pd.read_excel(xl, sheet_name=None)
    workspace = r"T:\work\giss\monthly\202304apr\gallaga\LRS\event tables Pro\Default.gdb"
    lrs_routes = r"T:\work\giss\monthly\202304apr\gallaga\LRS\event tables Pro\Default.gdb\TRNLRS\LRSN_Route"
    
    if arcpy.CheckExtension('LocationReferencing') == "Available":
        arcpy.CheckOutExtension("LocationReferencing")
        print("License checked out.")
    
    for sheet_name in workbook:
    
        if sheet_name.upper() not in [
            "E_STREETDIRECTION",
            "E_STREETSTATUS",
            "E_STREETOWNERSHIP",
            "E_STREETCLASS"
        ]:
            continue
    
        print(f"\n{sheet_name.upper()}")
    
        # df = workbook[sheet_name]
        lrs_form = LrsEventForm(xl, sheet_name)
        form_field_info = lrs_form.field_info()
    
        event_name = sheet_name
        output_feature = os.path.join(workspace, "TRNLRS", event_name)
    
        if not arcpy.Exists(output_feature):
            try:
                lrs_event = arcpy.locref.CreateLRSEvent(
                        parent_network=lrs_routes,
                        event_name=event_name,
                        geometry_type="LINE",
                        event_id_field="EventId",
                        route_id_field="RouteId",
                        from_date_field="FromDate",
                        to_date_field="ToDate",
                        loc_error_field="LocError",
                        measure_field="FromMeasure",
                        to_measure_field="ToMeasure",
                        event_spans_routes="NO_SPANS_ROUTES",
                    )[0]
    
                print(arcpy.GetMessages())
    
            except arcpy.ExecuteError:
                print(arcpy.GetMessages(2))
    
        # Add fields
        for info in form_field_info:
            field_name = info["FieldName"]
            if field_name not in LrsEventForm.standard_fields:
                print(f"Adding field '{field_name}'...")
    
                arcpy.AddField_management(
                    output_feature,
                    field_name=field_name,
                    field_type="TEXT" if "Date" not in info['Type (or Domain)'] else "DATE",
                    field_precision="",
                    field_scale="",
                    field_length=info["Length"],
                    field_alias=info["Alias"],
                    field_is_nullable="NULLABLE",
                    field_domain=""
                )
    
        # Add Editor Tracking Fields
        # add_editor_tracking_fields(output_feature)  # TODO: Decide if want to explicitly do this or do this via form
    
        # Add GlobalIDs
        print("Adding GlobalIDs...")
        arcpy.AddGlobalIDs_management(output_feature)
