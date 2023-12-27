import arcpy

import utils
import domains

from configparser import ConfigParser
from os import getcwd, environ
from os import getcwd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

CURRENT_DIR = getcwd()

NEW_DOMAINS = {
    "TRN_pavement_mark_priority": {
        "description": "",
        "field_type": "TEXT",
        "domain_type": "CODED",
    },
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    PC_NAME = environ['COMPUTERNAME']
    run_from = "SERVER" if "APP" in PC_NAME else "LOCAL"

    # TODO: Add to WEBGIS? web_ro?

    for dbs in [
        # [local_gdb, ],

        # WEBGIS features can use domains from SDEADM owner - don't need to create a domain for both SDEADM and WEBGIS

        # [config.get(run_from, "dev_rw"), config.get(run_from, "dev_ro"), config.get(run_from, "dev_web_ro_gdb")],

        [
            # config.get(run_from, "qa_rw"),
            # config.get(run_from, "qa_ro"),
            # config.get(run_from, "qa_web_ro_gdb")
        ],
        [
            config.get(run_from, "prod_rw"),
            config.get(run_from, "prod_ro"),
            config.get(run_from, "prod_web_ro_gdb")
        ],
    ]:

        if dbs:
            print(f"\nProcessing dbs: {', '.join(dbs)}...")

            for db in dbs:
                print(f"\nDATABASE: {db}")

                NEW_DOMAINS = {
                    "TRN_pavement_mark_priority": {
                        "description": "",
                        "field_type": "TEXT",
                        "domain_type": "CODED",
                    },
                }

                with arcpy.EnvManager(workspace=db):
                    for domain in NEW_DOMAINS:
                        domains.create_domain(
                            workspace=db,
                            domain_name=domain,
                            domain_description=NEW_DOMAINS[domain]["description"],
                            field_type=NEW_DOMAINS[domain]["field_type"],
                            domain_type=NEW_DOMAINS[domain]["domain_type"],
                        )
