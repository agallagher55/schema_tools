import arcpy
import os

from configparser import ConfigParser

import utils

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

FEATURE_DATASETS = ["HWADM.WaterNetwork", "HWADM.HWCS_network_infrastructure"]

REMOVE_FIELDS = ["LOCDESC"]

ADD_FIELDS = {
    "LOCATION": {
        "description": "",
        "alias": "Asset Location Details",
        "field_type": "TEXT",
        "field_length": "256",
        "nullable": "",
        "default": "",
        "domain": ""
    },
    "ADDRESS": {
        "description": "",
        "alias": "Nearest Address",
        "field_type": "TEXT",
        "field_length": "130",
        "nullable": "",
        "default": "",
        "domain": ""
    }
}

WEBGIS_SKIP_FEATURES = (
    "WEBGIS.HWCS_control_structure", "WEBGIS.HWCS_valve", "WEBGIS.HWCS_treatment_facility",
    "WEBGIS.HWCS_storm_mgmt_structure", "WEBGIS.HWCS_curb_corp_stop", "WEBGIS.HWCS_vent_line",
    "WEBGIS.HWCS_holding_tank", "WEBGIS.HWCS_pump", "WEBGIS.HWCS_chamber", "WEBGIS.HWCS_cso_structure",
    "WEBGIS.HWCS_fitting"
)


def update_fields(feature: str):
    current_fields = [x.name for x in arcpy.ListFields(feature)]

    print(f"\nRemoving fields from {feature}...")
    for remove_field in REMOVE_FIELDS:
        print(f"\tField to REMOVE: '{remove_field}'")

        if remove_field not in current_fields:
            # print(f"\t\tField, {remove_field}, not found in {feature}..!")
            continue

        arcpy.DeleteField_management(
            in_table=feature,
            drop_field=remove_field
        )
        print(arcpy.GetMessages(2))

    print(f"\nAdding fields to {feature}...")
    for add_field in ADD_FIELDS:
        print(f"\tField to ADD: {add_field}")

        # Check that field doesn't already exist
        if add_field in current_fields:
            # print(f"\t\tField, {add_field}, already exists in {feature}..!")
            continue

        print(f"\t\tAdding {add_field}...")
        arcpy.AddField_management(
            in_table=feature,
            field_name=add_field,  # Field Name
            field_type=ADD_FIELDS[add_field]["field_type"],  # Field Type
            field_length=ADD_FIELDS[add_field]["field_length"],  # Field Length (# of characters)
            field_alias=ADD_FIELDS[add_field]["alias"],  # Alias
            field_is_nullable=ADD_FIELDS[add_field]["nullable"],  # NULLABLE
            field_domain=ADD_FIELDS[add_field]["domain"]  # Domain
        )

        print(arcpy.GetMessages(2))


if __name__ == "__main__":
    local_gdb = utils.create_fgdb()

    for dbs in [
        # local_gdb,
        # [
        #     # config.get("SERVER", "dev_rw"),
        #     # config.get("SERVER", "dev_ro")  # Pause services: AGS_HalifaxWater_WGS84, Cityworks_Assets, Cityworks_Map, dde_map
        # ],
        [
            # config.get("SERVER", "qa_rw"),
            # config.get("SERVER", "qa_ro"),  # Pause services: AGS_HalifaxWater_WGS84, Cityworks_Assets, Cityworks_Map, dde_map
            # config.get("SERVER", "qa_web_ro"),
            # config.get("SERVER", "qa_web_ro_gdb")
        ]
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        # TODO: Stop services

        for db in dbs:

            webgis_features = []
            unused_webgis_features = []

            with arcpy.EnvManager(workspace=db):
                print(f"\nDATABASE: {db}")

                if db.endswith(".gdb"):
                    txtfile = open("webgis_features.txt", "r")
                    web_gdb_features = [x.replace("WEBGIS.", "").strip() for x in txtfile.readlines()]

                    for gdb_feature in web_gdb_features:
                        feature_path = os.path.join(db, gdb_feature)

                        print(f"\n\tFeature: {feature_path}")

                        if not arcpy.Exists(feature_path):
                            unused_webgis_features.append(gdb_feature)
                            print("Skipping...")
                            continue

                        update_fields(feature_path)

                    with open("webgis_features_only.txt", "w") as txtfile:
                        for row in unused_webgis_features:
                            txtfile.write(f"{row}\n")

                else:

                    for dataset in FEATURE_DATASETS:
                        print(f"\nDataset: {dataset}")

                        features = arcpy.ListFeatureClasses(feature_dataset=dataset)

                        for feature in features:

                            feature_path = os.path.join(db, dataset, feature)

                            if "WEBGIS" in db.upper():

                                feature_name = feature.replace("HWADM.", "WEBGIS.")  # WEBGIS.AST_water_valve
                                feature_path = os.path.join(db, feature_name)

                                if feature_name in WEBGIS_SKIP_FEATURES:
                                    print(f"\n**{feature_name} not found in WEBGIS. Skipping...")
                                    continue

                                else:
                                    webgis_features.append(feature_name)

                            print(f"\n\tFeature: {feature_path}")
                            update_fields(feature_path)

                    with open("webgis_features.txt", "w") as txtfile:
                        for row in webgis_features:
                            txtfile.write(f"{row}\n")

    # TODO: Run update scripts:
    #  E:\HRM\Scripts\Python\HW_Versioned_Data_Update\Scripts\HW_Versioned_CopyData.py  - Runs Friday night
    #  E:\HRM\Scripts\Python\HW_Versioned_Data_Update\Scripts\HW_Versioned_Data_Update.py  - Runs Saturday morning

    # TODO: Start services

    # TODO: make sure QA scripts have email notifications back in!
    # TODO: Update prod E:\HRM\Scripts\Python\HW_Versioned_Data_Update\Scripts\ with changes from QA (enumerate, etc.)
