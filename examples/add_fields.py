import os.path

import arcpy

from features import Table
import utils

from configparser import ConfigParser

from os import getcwd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

CURRENT_DIR = getcwd()

FEATURE = "SDEADM.AST_LIGHT_FIXTURE"  # TODO: this should be renamed so it doesn't clash with import

new_field_info = {
    "PWELID": {
        "description": "Power Light Enclosure ID",
        "alias": "Power Light Enclosure ID",
        "field_type": "TEXT",
        "field_length": "50",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    }
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    for dbs in [
        # [local_gdb],
        # [
        #     config.get("SERVER", "dev_rw"),
        #     config.get("SERVER", "dev_ro"),
        #  ],
        # [
        #     config.get("SERVER", "qa_rw"),
        #     config.get("SERVER", "qa_ro")
        # ],
        [
            config.get("SERVER", "prod_rw"),
            config.get("SERVER", "prod_ro")
        ],

    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db.endswith(".gdb"):
                FEATURE = FEATURE.replace("SDEADM.", "")

            print(f"Feature: {FEATURE}")

            with arcpy.EnvManager(workspace=db):

                desc = arcpy.Describe(FEATURE)

                my_feature = Table(db, desc.baseName)
                current_fields = [x.name for x in arcpy.ListFields(FEATURE)]

                # TODO: Stop services

                for field in new_field_info:
                    print(f"\tField to add: {field}")

                    # Check that field doesn't already exist

                    if field in current_fields:
                        print(f"Field, {field} already exists in {FEATURE}..!")
                        # continue

                    my_feature.add_field(
                        field_name=field,
                        field_type=new_field_info[field]["field_type"],
                        length=new_field_info[field]["field_length"],
                        alias=new_field_info[field]["alias"],
                        domain_name=new_field_info[field]["domain"]
                    )

                    # TODO: Index Field
                    # try:
                    print("Adding index...")
                    arcpy.AddIndex_management(
                        in_table=my_feature.feature_name,
                        fields=field,
                        index_name=f"index_{field}",
                        ascending="ASCENDING"
                    )
                    # except arcpy.ExecuteError:
                    #     arcpy_msg = arcpy.GetMessages(2)
                    #     print(arcpy_msg)

                # TODO: Start services
                # * Had to manually unlock with SDE connection
