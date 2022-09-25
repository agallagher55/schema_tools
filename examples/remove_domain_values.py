import arcpy

import utils
import domains

from datetime import datetime

arcpy.SetLogHistory(False)

start_time = datetime.now()
print(start_time.strftime('%Y/%m/%d %H:%M:%S'))


def with_msgs(command):
    print('-' * 100)
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)


# DEV
dev_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RW_SDEADM.sde"
dev_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RO_SDEADM.sde"
# dev_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_DEV_RO.sde"  # Only need to include when adding a new domain to a field
dev_gdbs = [dev_ro, dev_rw]

# QA
qa_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RW_SDEADM.sde"
qa_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_SDEADM.sde"
# qa_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_webgis.sde"  # Only need to include when adding a new domain to a field
qa_gdbs = [qa_rw, qa_ro]

# PROD
prod_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RW_SDEADM.sde"
prod_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RO_SDEADM.sde"
# prod_ro_web = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_PROD_RO_win.sde"  # Only need to include when adding a new domain to a field
prod_gdbs = [prod_rw, prod_ro]

# WEB
# web gdbs are in intermediate workspace and also used to publish some web services from

# TODO: add WEBGIS dbs and check for adding new domain. If new domain, add to WEBGIS connections

dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"
prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_Prod\fgdbs\web_RO.gdb"

web_gdbs = [
    prod_web_ro_gdb,
    dev_web_ro_gdb,
    qa_web_ro_gdb
]

db_connections = [dev_gdbs, qa_gdbs, prod_gdbs, web_gdbs]


def check_connections(db_connections: [[]]):
    # Make sure all db connection files are valid
    print(f"\nChecking connections...")

    fails = []
    success = []

    for connections in db_connections:
        for connection in connections:

            if not arcpy.Exists(connection):
                fails.append(connection)

            else:
                success.append(connection)

    return {"valid": success, "invalid": fails}


if __name__ == "__main__":
    DOMAIN_NAME = "LND_grass_class"

    REMOVE_CODE_VALUES = {
        "N/A": "Not Applicable",
    }

    # Create scratch workspace in working folder
    WORKING_FOLDER = r"T:\work\giss\monthly\202208aug\gallaga\Grass Schema\sys_admin-main (2)\sys_admin-main"

    # TODO: Use COPY GP tool to bring SDE feature with domain to scratch geodatabase - this will transfer domains for testing
    SCRATCH_GDB = utils.create_fgdb(WORKING_FOLDER)

    print(f"\nAltering Domain '{DOMAIN_NAME}'...")

    # connections = check_connections([
    #     [SCRATCH_GDB],
    #     # dev_gdbs,
    #     # qa_gdbs,
    #     # prod_gdbs,
    #     # web_gdbs
    #     ]
    # )

    # if connections.get("invalid"):
    #     raise IndexError(f"Invalid connection(s) found: {', '.join(connections.get('invalid'))}")

    for dbs in [
        # [SCRATCH_GDB],
        dev_gdbs,
        # qa_gdbs,
        # prod_gdbs,
        # web_gdbs
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\n\tDatabase: {db}")

            # Check that domain is found in database connection
            domain_found, db_domains = domains.domain_in_db(db, DOMAIN_NAME)

            if not domain_found:
                raise ValueError(f"Did not find domain '{DOMAIN_NAME}' in db. Found domains: {', '.join(db_domains)}")

            for code in REMOVE_CODE_VALUES:
                domains.remove_code_value(db, DOMAIN_NAME, code)

    finish_time = datetime.now()
    print(f"\nFinished: {finish_time.strftime('%Y/%m/%d %H:%M:%S')}")

    # TODO: Stop, Start services that use domain to allow for web users to see new domain values