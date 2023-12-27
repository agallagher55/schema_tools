import arcpy

from features import Feature

import utils

from configparser import ConfigParser
from os import getcwd, environ
from os import getcwd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

CURRENT_DIR = getcwd()

FEATURE = "SDEADM.TRN_pavement_marking"  # TODO: this should be renamed so it doesn't clash with import

SPATIAL_REFERENCE = None

new_field_info = {
    "PRIORITY": {
        "description": "Pavement marking is listed as regular or priority",
        "alias": "Priority",
        "field_type": "TEXT",
        "field_length": "5",
        "nullable": "NULLABLE",
        "default": "",
        "domain": "TRN_pavement_mark_priority"
    },
    "BWL_1_8_M": {
        "description": "Total length in metres",
        "alias": "Broken White Line (1.8m)",
        "field_type": "DOUBLE",
        # "field_length": "50",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    },
    "BWL_0_5_M": {
        "description": "Total length in metres",
        "alias": "Broken White Line (0.5m)",
        "field_type": "DOUBLE",
        # "field_length": "50",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    },
    "BWL_3_0_M": {
        "description": "Total length in metres",
        "alias": "Broken White Line (3m)",
        "field_type": "DOUBLE",
        # "field_length": "50",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    },
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    PC_NAME = environ['COMPUTERNAME']
    run_from = "SERVER" if "APP" in PC_NAME else "LOCAL"

    # TODO: Add to WEBGIS? web_ro?

    for dbs in [
        [local_gdb, ],
        # [config.get(run_from, "dev_rw"), config.get(run_from, "dev_ro"), config.get(run_from, "dev_web_ro_gdb")],
        # [
        #     config.get(run_from, "qa_rw"),
        #     config.get(run_from, "qa_ro"),
        #     config.get(run_from, "qa_web_ro_gdb")
        # ],
        # [config.get(run_from, "prod_rw"), config.get(run_from, "prod_ro"), config.get(run_from, "prod_web_ro_gdb")],

        # SQL SERVER
        [
            # config.get("SQL SERVER", "qa_rw"),
            # config.get("SQL SERVER", "qa_ro"),
            # config.get("SQL SERVER", "qa_web_ro"),
            # config.get("SQL SERVER", "qa_web_ro_gdb")
        ],
        [
            # config.get(run_from, "prod_rw"),
            # config.get(run_from, "prod_ro"),
            # config.get(run_from, "prod_ro_web"),
            # config.get(run_from, "prod_web_ro_gdb")
        ],
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db.endswith(".gdb"):
                FEATURE = FEATURE.replace("SDEADM.", "")

            elif "WEBGIS" in db.upper():
                FEATURE = FEATURE.replace("SDEADM.", "WEBGIS.")

            print(f"Feature: {FEATURE}")

            with arcpy.EnvManager(workspace=db):

                # Check if feature exists
                if not arcpy.Exists(FEATURE):
                    raise ValueError(f"\tFeature, '{FEATURE}', does not exist.")

                desc = arcpy.Describe(FEATURE)

                my_feature = Feature(db, desc.baseName, "POINT")
                current_fields = [x.name for x in arcpy.ListFields(FEATURE)]

                # TODO: Stop services

                for field in new_field_info:
                    print(f"\nField to add: '{field}'")

                    # Check that field doesn't already exist

                    if field in current_fields:
                        print(f"Field, {field} already exists in {FEATURE}..!")
                        continue

                    my_feature.add_field(
                        field_name=field,
                        field_type=new_field_info[field]["field_type"],
                        length=new_field_info[field].get("field_length", "#"),
                        alias=new_field_info[field]["alias"],
                        domain_name=new_field_info[field]["domain"]
                    )

                # TODO: Start services
                # * Had to manually unlock with SDE connection
