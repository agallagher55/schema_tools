import arcpy

from features import Feature
import utils

from configparser import ConfigParser

from os import getcwd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

CURRENT_DIR = getcwd()

FEATURE = "SDEADM.TRN_bus_stop"  # TODO: this should be renamed so it doesn't clash with import

SPATIAL_REFERENCE = None

new_field_info = {
    "INSP_DATE": {
        "description": "The date that the bus stop was last inspected by Halifax Transit Staff",
        "alias": "Date Last Inspected",
        "field_type": "DATE",
        # "field_length": "50",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    }
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)
    
    # TODO: Add to WEBGIS? web_ro?

    for dbs in [
        # [local_gdb],
        # [
        #     config.get("SERVER", "dev_rw"),
        #     config.get("SERVER", "dev_ro"),
        #  ],
        [
            config.get("SERVER", "qa_rw"),
            config.get("SERVER", "qa_ro")
        ],
        # [
        #     config.get("SERVER", "prod_rw"),
        #     config.get("SERVER", "prod_ro")
        # ],

    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db.endswith(".gdb"):
                FEATURE = FEATURE.replace("SDEADM.", "")

            print(f"Feature: {FEATURE}")

            with arcpy.EnvManager(workspace=db):

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
