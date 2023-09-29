import arcpy

import features
import utils

from configparser import ConfigParser

from os import getcwd, environ

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

REMOVE_DOMAINS = {
    "SDEADM.TRN_traffic_study": ["STREETNAME4", "STREETNAME5"],
}


CURRENT_DIR = getcwd()


if __name__ == "__main__":
    from datetime import datetime

    print(datetime.now())

    for dbs in [
        # [utils.create_fgdb(CURRENT_DIR)],
        # [config.get("SERVER", "dev_rw"), config.get("SERVER", "dev_ro"), config.get("SERVER", "dev_web_ro_gdb")],
        [
            config.get("SERVER", "qa_rw"),
            config.get("SERVER", "qa_ro"),
            config.get("SERVER", "qa_web_ro_gdb")
        ],
        # [config.get("SERVER", "prod_rw"), config.get("SERVER", "prod_ro"), config.get("SERVER", "prod_web_ro_gdb")],
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db == local_gdb:

                PC_NAME = environ['COMPUTERNAME']
                prod_sde = config.get("SERVER", "prod_rw") if "APP" in PC_NAME else config.get("LOCAL", "prod_rw")

                with arcpy.EnvManager(workspace=prod_sde):
                    features.transfer_features(list(REMOVE_DOMAINS.keys()), local_gdb)

            with arcpy.EnvManager(workspace=db):
                for feature in REMOVE_DOMAINS:
                    remove_fields = REMOVE_DOMAINS[feature]

                    if db == local_gdb:
                        feature = feature.replace("SDEADM.", "")

                    features.remove_domain(feature, remove_fields)

    print(datetime.now())
