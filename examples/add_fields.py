import os.path

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

FEATURE = "SDEADM.LND_OFF_LEASH"  # TODO: this should be renamed so it doesn't clash with import

new_field_info = {
    "PARK_ID": {
        "description": "Foreign key to identify persistent relationship of dog park to HRM Park",
        "alias": "Park ID",
        "field_type": "LONG",
        "field_length": "",
        "nullable": "NULLABLE",
        "default": "",
        "domain": ""
    },
    "ALT_NAME": {
        "description": "Unofficial name as local communities refer to the off-leash parks, areas, and sport fields",
        "alias": "Alternative Name",
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
        [local_gdb],
        # [config.get("SERVER", "dev_rw")],
        # [config.get("SERVER", "qa_rw")],
        # [config.get("SERVER", "prod_rw")],

    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db.endswith(".gdb"):
                FEATURE = FEATURE.replace("SDEADM.", "")

            print(f"Feature: {FEATURE}")

            with arcpy.EnvManager(workspace=db):

                desc = arcpy.Describe(FEATURE)

                my_feature = Feature(db, desc.baseName, desc.dataType, desc.spatialReference)
                current_fields = [x.name for x in arcpy.ListFields(FEATURE)]

                for field in new_field_info:
                    print(f"\tField to add: {field}")

                    # Check that field doesn't already exist

                    if field in current_fields:
                        print(f"Field, {field} already exists in {FEATURE}..!")
                        continue

                    my_feature.add_field(
                        field_name=field,
                        field_type=new_field_info[field]["field_type"],
                        length=new_field_info[field]["field_length"],
                        alias=new_field_info[field]["alias"],
                        nullable=new_field_info[field]["nullable"],
                        domain_name=new_field_info[field]["domain"]
                    )
