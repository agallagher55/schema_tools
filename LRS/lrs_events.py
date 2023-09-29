import os
import arcpy

import pandas as pd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)


class LrsEventForm:
    standard_fields = ("OBJECTID", "FROMDATE", "TODATE", "EVENTID", "ROUTEID", "LOCERROR", "SHAPE")

    event_behvaiours_sheet = "Event Behaviors"
    event_behaviours_start_row = 2

    def __init__(self, source, sheet_name):
        self.source = source
        self.sheet_name = sheet_name

        self.df = pd.read_excel(source, sheet_name=sheet_name)
        self.df = self.df.fillna('')

        self.df_event_behaviours = pd.read_excel(self.source, sheet_name=LrsEventForm.event_behvaiours_sheet,
                                                 header=LrsEventForm.event_behaviours_start_row)

        self.event_field = self.get_event_field()

    def get_event_field(self):
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

        # TODO: Translate field types into types recognized by AddField GP tool

        return field_info

    def event_behviours(self):
        # Find row with Activity and Rule values
        return self.df_event_behaviours.to_dict('records')


if __name__ == "__main__":
    from utils import create_fgdb

    event_names = ["E_HospitalRoute", ]

    skip_events = []

    xl = r"T:\work\giss\monthly\202309sep\gallaga\LRS_hospital_routes\Create new LRS Event Hospital Routes 14Sep2023.xlsx"

    workbook = pd.read_excel(xl, sheet_name=None)
    workspace = create_fgdb()

    lrs_routes = os.path.join(workspace, "TRNLRS", "LRSN_Route")

    if not arcpy.Exists(lrs_routes):
        raise ValueError(f"ERROR: '{lrs_routes}' does not exist.")

    if arcpy.CheckExtension('LocationReferencing') == "Available":
        arcpy.CheckOutExtension("LocationReferencing")
        print("License checked out.")

    for sheet_name in event_names:

        if sheet_name.upper() in skip_events:
            continue

        print(f"\nEvent: {sheet_name.upper()}")

        # df = workbook[sheet_name]
        lrs_form = LrsEventForm(xl, sheet_name)
        form_field_info = lrs_form.field_info()

        event_behaviours = lrs_form.event_behviours()

        event_name = sheet_name
        output_event_feature = os.path.join(workspace, "TRNLRS", event_name)

        if not arcpy.Exists(output_event_feature):
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
        current_event_fields = [x.name.upper() for x in arcpy.ListFields(output_event_feature)]

        for info in form_field_info:

            field_name = info["FieldName"]

            if field_name.upper() in current_event_fields:
                continue

            if field_name not in LrsEventForm.standard_fields:
                print(f"\nAdding field '{field_name}'...")

                arcpy.AddField_management(
                    output_event_feature,
                    field_name=field_name,
                    field_type="TEXT" if "Date" not in info['Type'] else "DATE",
                    field_precision="",
                    field_scale="",
                    field_length=info["Length"],
                    field_alias=info["Alias"],
                    field_is_nullable="NULLABLE",
                    field_domain=info['Domain']
                )

        # Add event behaviours
        print("\nApplying event behaviours...")
        event_behaviour_ruleset = lrs_form.event_behviours()
        event_behviour_dict = {item['Activity']: item['Rule'] for item in event_behaviour_ruleset}

        arcpy.locref.ModifyEventBehaviorRules(
            in_feature_class=output_event_feature,
            calibrate_rule=event_behviour_dict['Calibrate Route'],
            retire_rule=event_behviour_dict['Retire Route'],
            extend_rule=event_behviour_dict['Extend Route'],
            reassign_rule=event_behviour_dict['Reassign Route'],
            realign_rule=event_behviour_dict['Realign Route'],
            reverse_rule=event_behviour_dict['Reverse Route'],
            carto_realign_rule=event_behviour_dict['Carto Realign Route']
        )
        print(arcpy.GetMessages())

        # Apply Editor Tracking
        print(f"\nApplying editor tracking to {output_event_feature}...")

        if arcpy.Describe(output_event_feature).editorTrackingEnabled:
            print(f"\t{output_event_feature} already had Editor Tracking Enabled!")

        arcpy.EnableEditorTracking_management(
            output_event_feature,
            "ADDBY",
            "ADDDATE",
            "MODBY",
            "MODDATE",
            "NO_ADD_FIELDS",
            "UTC"
        )
        print(arcpy.GetMessages())

        # Add GlobalIDs
        print("Adding GlobalIDs...")
        arcpy.AddGlobalIDs_management(output_event_feature)
