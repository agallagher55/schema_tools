import arcpy

from datetime import datetime

arcpy.SetLogHistory(False)

s = datetime.now()
print(s.strftime('%Y/%m/%d %H:%M:%S'))


def with_msgs(command):
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)


SCRATCH_GDB = r"T:\work\giss\monthly\202207jul\gallaga\Add Domain Codes Values\scripts\Scratch.gdb"
# TODO: Use Feature Class to Feature Class to bring SDE feature with domain to scratch geodatabase - this will transfer domains for testing - **Confirm

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
dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
# qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA107\fgdbs\web_RO.gdb"  # TODO: No more QA107?
qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"
prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_Prod107\fgdbs\web_RO.gdb"
web_gdbs = [
    prod_web_ro_gdb,
    dev_web_ro_gdb,
    qa_web_ro_gdb
]

db_connections = [dev_gdbs, qa_gdbs, prod_gdbs, web_gdbs]

# Make sure all db connection files are valid
fails = []
success = []
# for connections in db_connections:
#     for connection in connections:
#
#         if not arcpy.Exists(connection):
#             fails.append(connection)
#
#         else:
#             success.append(connection)
#
# if fails:
#     raise ValueError(f"Failed to find geodatabases: '{', '.join(fails)}'")


def domain_in_db(db, domain):
    # Make sure domain exists in database
    domains = [domain.name for domain in arcpy.da.ListDomains(db)]

    if domain not in domains:
        return False, domains

    return True, domains


if __name__ == "__main__":
    EXISTING_DOMAIN_NAME = "TRN_bike_Infra_type"

    for dbs in [
        # [SCRATCH_GDB],
        # dev_gdbs,
        # qa_gdbs,
        # prod_gdbs,
        web_gdbs
    ]:
        for db in dbs:
            print(f"\n\nDatabase: {db}")
            domain_found, db_domains = domain_in_db(db, EXISTING_DOMAIN_NAME)

            if not domain_found:
                raise ValueError(f"Did not find domain '{EXISTING_DOMAIN_NAME}' in db. Found domains: {', '.join(db_domains)}")

            print(f"Adding coded domain values to '{EXISTING_DOMAIN_NAME}'...")
            with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_PROTBL", "Interim Protected Bike Lane"))
            with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_MUPATH", "Interim Multi-Use Pathway"))
            with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_QUIET", "Interim Bike Improvements on Quiet Streets"))
            with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "HELPCONN", "Helpful Connections"))

    f = datetime.now()
    print(f.strftime('%Y/%m/%d %H:%M:%S'))

    # TODO: Stop, Start services that use domain to allow for web users to see new domain values
