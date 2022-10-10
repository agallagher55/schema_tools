import arcpy

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
    "HRM_DEPT": "REAL ESTATE",
    "TRANSASSET": "LND",  # LND
    "SOURCE": "Transaction Summary",  # Not a Domain
    "SACC": "IN"  # IN
}

SUBTYPE_CODES = ['1: Acquisition', '2: Disposal']


if __name__ == "__main__":
    
    FEATURE = "SDEADM.LND_ACQUISITION_DISPOSAL"
    
    # for connection in web_gdbs:
    for connection in [
        # dev_rw, dev_ro, dev_web_ro
        # qa_rw, qa_ro, qa_web_ro,
        prod_rw, prod_ro, prod_ro_web

    ]:
        print(f"\nProcessing {connection} workspace...")

        with arcpy.EnvManager(workspace=connection):

            for field_name, field_default in FIELD_DEFAULTS.items():
                print(f"\tSetting {field_name} default to '{field_default}'...")

                result = arcpy.AssignDefaultToField_management(
                    in_table=FEATURE,
                    field_name=field_name,
                    default_value=field_default,
                    subtype_code=SUBTYPE_CODES,
                    clear_value="DO_NOT_CLEAR"
                )[0]
