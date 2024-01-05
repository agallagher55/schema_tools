import arcpy

from os import environ

from configparser import ConfigParser

from os import getcwd, environ

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

# DEV
dev_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RW_SDEADM.sde"
dev_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RO_SDEADM.sde"
dev_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_DEV_RO.sde"  # Only need to include when adding a new domain to a field
dev_gdbs = [dev_ro, dev_rw]

# QA
qa_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RW_SDEADM.sde"
qa_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_SDEADM.sde"
qa_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_webgis.sde"  # Only need to include when adding a new domain to a field
qa_gdbs = [qa_rw, qa_ro]

# PROD
prod_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RW_SDEADM.sde"
prod_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RO_SDEADM.sde"
prod_ro_web = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_PROD_RO_win.sde"  # Only need to include when adding a new domain to a field
prod_gdbs = [prod_rw, prod_ro]

# web gdbs are in intermediate workspace and also used to publish some web services from
# dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
# qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"
# prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_Prod\fgdbs\web_RO.gdb"

web_gdbs = [
    # prod_web_ro_gdb,
    # dev_web_ro_gdb,
    # qa_web_ro_gdb
]

FIELD_DEFAULTS = {
    "SPEC_TYPE": "GRASS",
}

# SUBTYPE_CODES = ['1: Acquisition', '2: Disposal']
SUBTYPE_CODES = ['1: Natural Area Descriptions']

if __name__ == "__main__":

    PC_NAME = environ['COMPUTERNAME']
    run_from = "SERVER" if "APP" in PC_NAME else "LOCAL"

    SDE = r"E:\HRM\Scripts\SDE\SQL\Prod\prod_RW_sdeadm.sde"
    FEATURE = "SDEADM.LND_grass_contract"
    # FEATURE = "SDEADM.LND_ACQUISITION_DISPOSAL"

    # for connection in web_gdbs:
    for dbs in [
        # WEBGIS features can use domains from SDEADM owner - don't need to create a domain for both SDEADM and WEBGIS

        # [
        # config.get(run_from, "dev_rw"),
        # config.get(run_from, "dev_ro"),
        # ],
        # [
            # config.get(run_from, "qa_rw"),
            # config.get(run_from, "qa_ro"),
            # config.get(run_from, "qa_web_ro_gdb")
        # ],
        [
            config.get(run_from, "prod_rw"),
        #     config.get(run_from, "prod_ro"),
        #     config.get(run_from, "prod_web_ro_gdb")
        ],
    ]:
        if dbs:
            print(f"\nProcessing dbs: {', '.join(dbs)}...")

            for db in dbs:

                print(f"\nProcessing {db} workspace...")

                with arcpy.EnvManager(workspace=db):

                    # Get subtypes
                    subtypes = arcpy.da.ListSubtypes(FEATURE)
                    subtype_codes = [f'{s}: {subtypes[s]["Name"]}' for s in subtypes]

                    for field_name, field_default in FIELD_DEFAULTS.items():
                        print(f"\tSetting {field_name} default to '{field_default}'...")

                        result = arcpy.AssignDefaultToField_management(
                            in_table=FEATURE,
                            field_name=field_name,
                            default_value=field_default,
                            subtype_code=SUBTYPE_CODES,
                            clear_value="DO_NOT_CLEAR"
                        )[0]
