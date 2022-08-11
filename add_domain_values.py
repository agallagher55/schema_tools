import arcpy

from datetime import datetime

arcpy.SetLogHistory(False)

start_time = datetime.now()
print(start_time.strftime('%Y/%m/%d %H:%M:%S'))


def with_msgs(command):
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)


# TODO: Create scratch workspace in working folder

SCRATCH_GDB = r"T:\work\giss\monthly\202207jul\gallaga\Add Domain Codes Values\scripts\Scratch.gdb"
# TODO: Use COPY GP tool to bring SDE feature with domain to scratch geodatabase - this will transfer domains for testing

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


def copy_domain_feature(feature, workspace):
    arcpy.Copy_management(
        r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.LND_hrm_parcel_parks\SDEADM.LND_hrm_parcel",
        r"T:\work\giss\monthly\202207jul\gallaga\Add Domain Codes Values\scripts\Scratch.gdb\LND_hrm_parcel",
        "FeatureClass",
        "SDEADM.LND_hrm_parcel_parks FeatureDataset LND_hrm_parcel_parks #;SDEADM.LND_hrm_parcel_has_class RelationshipClass LND_hrm_parcel_has_class #;SDEADM.LND_hrm_park_has_parcel RelationshipClass LND_hrm_park_has_parcel #;SDEADM.LND_hrm_parcel_LND_LAND_PHOTO RelationshipClass LND_hrm_parcel_LND_LAND_PHOTO #;SDEADM.LND_group_has_hrm_parcel RelationshipClass LND_group_has_hrm_parcel #;SDEADM.LND_hrm_park FeatureClass LND_hrm_park #;SDEADM.LND_hrm_park_has_photo RelationshipClass LND_hrm_park_has_photo #;SDEADM.LND_hrm_parcel_has_acq_disp RelationshipClass LND_hrm_parcel_has_acq_disp #;SDEADM.LND_LAND_CLASSIFICATION TableDataset LND_LAND_CLASSIFICATION #;SDEADM.LND_LAND_PHOTO TableDataset LND_LAND_PHOTO #;SDEADM.LND_LAND_GROUP TableDataset LND_LAND_GROUP #;SDEADM.LND_ACQUISITION_DISPOSAL TableDataset LND_ACQUISITION_DISPOSAL #;SDEADM.BLD_building_has_AcqDisp RelationshipClass BLD_building_has_AcqDisp #;SDEADM.BLD_BUILDING TableDataset BLD_BUILDING #;SDEADM.BLD_building_has_polygon RelationshipClass BLD_building_has_polygon #;SDEADM.BLD_building_has_symbol RelationshipClass BLD_building_has_symbol #;SDEADM.BLD_building_has_group_link RelationshipClass BLD_building_has_group_link #;SDEADM.BLD_building_has_use RelationshipClass BLD_building_has_use #;SDEADM.BLD_building_has_civic_link RelationshipClass BLD_building_has_civic_link #;SDEADM.BLD_building_polygon FeatureClass BLD_building_polygon #;SDEADM.BLD_building_symbol FeatureClass BLD_building_symbol #;SDEADM.BLD_building_group_link TableDataset BLD_building_group_link #;SDEADM.BLD_BUILDING_USE TableDataset BLD_BUILDING_USE #;SDEADM.BLD_BUILDING_CIVIC_LINK TableDataset BLD_BUILDING_CIVIC_LINK #;SDEADM.BLD_building_group_has_link RelationshipClass BLD_building_group_has_link #;SDEADM.BLD_BUILDING_GROUP TableDataset BLD_BUILDING_GROUP #;LND_land_assetcode 'CV domain' LND_land_assetcode #;AAA_asset_owner 'CV domain' AAA_asset_owner #;AAA_asset_locgen 'CV domain' AAA_asset_locgen #;AAA_yes_no 'CV domain' AAA_yes_no #;AAA_asset_conf 'CV domain' AAA_asset_conf #;LND_modified_type 'CV domain' LND_modified_type #;AAA_asset_group 'CV domain' AAA_asset_group #;AAA_asset_stat 'CV domain' AAA_asset_stat #;AAA_asset_crit 'CV domain' AAA_asset_crit #;AAA_asset_performrat 'CV domain' AAA_asset_performrat #;AAA_asset_condrat 'CV domain' AAA_asset_condrat #;AAA_operator_asset 'CV domain' AAA_operator_asset #;LND_land_source 'CV domain' LND_land_source #;SourceAccuracy 'CV domain' SourceAccuracy #;Bldg_Official_Name 'CV domain' Bldg_Official_Name #;LND_land_park_maint 'CV domain' LND_land_park_maint #;LND_land_park_type 'CV domain' LND_land_park_type #;LND_land_class 'CV domain' LND_land_class #;LND_land_asset_type 'CV domain' LND_land_asset_type #;LND_land_serv_cat 'CV domain' LND_land_serv_cat #;LND_land_acq_type 'CV domain' LND_land_acq_type #;LND_land_acq_purp 'CV domain' LND_land_acq_purp #;AAA_hrm_dept 'CV domain' AAA_hrm_dept #;AAA_asset_trans_type 'CV domain' AAA_asset_trans_type #;LND_land_disp_type 'CV domain' LND_land_disp_type #;Bldg_TBL_source 'CV domain' Bldg_TBL_source #;Bldg_nbc_part 'CV domain' Bldg_nbc_part #;Bldg_fsa_code 'CV domain' Bldg_fsa_code #;Bldg_alarm_sprinkler_system 'CV domain' Bldg_alarm_sprinkler_system #;Bldg_structure_type 'CV domain' Bldg_structure_type_1 #;Bldg_construction_type 'CV domain' Bldg_construction_type #;Bldg_fcode 'CV domain' Bldg_fcode #;Bldg_FC_source 'CV domain' Bldg_FC_source #;Bldg_symbol_fcode 'CV domain' Bldg_symbol_fcode #;Bldg_BLIS_uses 'CV domain' Bldg_BLIS_uses #;Bldg_occclass 'CV domain' Bldg_occclass #;Bldg_BLRC_uses 'CV domain' Bldg_BLRC_uses #;Bldg_BLTR_uses 'CV domain' Bldg_BLTR_uses #;Bldg_BLRS_uses 'CV domain' Bldg_BLRS_uses #;Bldg_BLCM_uses 'CV domain' Bldg_BLCM_uses #;Bldg_BLID_uses 'CV domain' Bldg_BLID_uses #;Bldg_BLAF_uses 'CV domain' Bldg_BLAF_uses #;Bldg_BLIT_uses 'CV domain' Bldg_BLIT_uses #")


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


def domain_in_db(db, domain):
    # Make sure domain exists in database
    domains = [domain.name for domain in arcpy.da.ListDomains(db)]

    if domain not in domains:
        return False, domains

    return True, domains


if __name__ == "__main__":
    DOMAIN_NAME = "AAA_operator_asset"
    ADD_CODE_VALUES = {
        "FR11961": "Francois Malenfant",
    }
    
    print(f"\nAltering Domain '{DOMAIN_NAME}'...")

    # connections = check_connections([
    #     [SCRATCH_GDB],
    #     dev_gdbs,
    #     qa_gdbs,
    #     prod_gdbs,
    #     web_gdbs]
    # )
    #
    # if connections.get("invalid"):
    #     raise IndexError(f"Invalid connection(s) found: {', '.join(connections.get('invalid'))}")

    for dbs in [
        # [SCRATCH_GDB],
        # dev_gdbs,
        # qa_gdbs,
        prod_gdbs,
        # web_gdbs
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\n\tDatabase: {db}")

            # Check that domain is found in database connection
            domain_found, db_domains = domain_in_db(db, DOMAIN_NAME)

            if not domain_found:
                raise ValueError(f"Did not find domain '{DOMAIN_NAME}' in db. Found domains: {', '.join(db_domains)}")

            print(f"\tAdding coded domain values to domain '{DOMAIN_NAME}'...")
            for code_value in ADD_CODE_VALUES:
                new_code = code_value
                new_value = ADD_CODE_VALUES[code_value]
                
                print(f"Adding domain code, value: {new_code}, {new_value}...")

                with_msgs(arcpy.AddCodedValueToDomain_management(
                    in_workspace=db,
                    domain_name=DOMAIN_NAME,
                    code=new_code,
                    code_description=new_value)
                )

            # with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_PROTBL", "Interim Protected Bike Lane"))
            # with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_MUPATH", "Interim Multi-Use Pathway"))
            # with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "INT_QUIET", "Interim Bike Improvements on Quiet Streets"))
            # with_msgs(arcpy.AddCodedValueToDomain_management(db, EXISTING_DOMAIN_NAME, "HELPCONN", "Helpful Connections"))

    finish_time = datetime.now()
    print(finish_time.strftime('%Y/%m/%d %H:%M:%S'))

    # TODO: Stop, Start services that use domain to allow for web users to see new domain values
