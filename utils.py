import arcpy
import os


def create_fgdb(out_folder_path, out_name="scratch.gdb"):
    """
    Create scratch workspace (gdb)

    :param out_folder_path:
    :param out_name:
    :return: path to file geodatabase
    """

    print(f"\nCreating File Geodatabase '{out_name}'...")
    workspace_path = os.path.join(out_folder_path, out_name)

    if arcpy.Exists(workspace_path):
        print(f"\tFile Geodatabase already exists!")
        return workspace_path

    fgdb = arcpy.CreateFileGDB_management(out_folder_path, out_name).getOutput(0)
    print("\tFile Geodatabase created!")

    return fgdb


def copy_feature(copy_feature, workspace):
    """
    - Copy Features, carrying over domains
    :param copy_feature:
    :param workspace:
    :return:
    """

    print(f"\nCopying '{copy_feature}' to {workspace}...")

    feature_name = arcpy.Describe(copy_feature).name.lstrip("SDEADM.")  # Remove SDEADM.
    output_feature = os.path.join(workspace, feature_name)

    with arcpy.EnvManager(workspace=workspace):
        workspace_features = arcpy.ListFeatureClasses()

        # Check if feature already exists in workspace
        if feature_name not in workspace_features:

            arcpy.Copy_management(
                in_data=copy_feature,
                out_data=output_feature
            )

            return output_feature

        else:
            print(f"\t*{feature_name} already exists in {workspace}.")

    # arcpy.Copy_management(
    #     r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.LND_hrm_parcel_parks\SDEADM.LND_hrm_parcel",
    #     r"T:\work\giss\monthly\202207jul\gallaga\Add Domain Codes Values\scripts\Scratch.gdb\LND_hrm_parcel",
    #     "FeatureClass",
    #     "SDEADM.LND_hrm_parcel_parks FeatureDataset LND_hrm_parcel_parks #;SDEADM.LND_hrm_parcel_has_class RelationshipClass LND_hrm_parcel_has_class #;SDEADM.LND_hrm_park_has_parcel RelationshipClass LND_hrm_park_has_parcel #;SDEADM.LND_hrm_parcel_LND_LAND_PHOTO RelationshipClass LND_hrm_parcel_LND_LAND_PHOTO #;SDEADM.LND_group_has_hrm_parcel RelationshipClass LND_group_has_hrm_parcel #;SDEADM.LND_hrm_park FeatureClass LND_hrm_park #;SDEADM.LND_hrm_park_has_photo RelationshipClass LND_hrm_park_has_photo #;SDEADM.LND_hrm_parcel_has_acq_disp RelationshipClass LND_hrm_parcel_has_acq_disp #;SDEADM.LND_LAND_CLASSIFICATION TableDataset LND_LAND_CLASSIFICATION #;SDEADM.LND_LAND_PHOTO TableDataset LND_LAND_PHOTO #;SDEADM.LND_LAND_GROUP TableDataset LND_LAND_GROUP #;SDEADM.LND_ACQUISITION_DISPOSAL TableDataset LND_ACQUISITION_DISPOSAL #;SDEADM.BLD_building_has_AcqDisp RelationshipClass BLD_building_has_AcqDisp #;SDEADM.BLD_BUILDING TableDataset BLD_BUILDING #;SDEADM.BLD_building_has_polygon RelationshipClass BLD_building_has_polygon #;SDEADM.BLD_building_has_symbol RelationshipClass BLD_building_has_symbol #;SDEADM.BLD_building_has_group_link RelationshipClass BLD_building_has_group_link #;SDEADM.BLD_building_has_use RelationshipClass BLD_building_has_use #;SDEADM.BLD_building_has_civic_link RelationshipClass BLD_building_has_civic_link #;SDEADM.BLD_building_polygon FeatureClass BLD_building_polygon #;SDEADM.BLD_building_symbol FeatureClass BLD_building_symbol #;SDEADM.BLD_building_group_link TableDataset BLD_building_group_link #;SDEADM.BLD_BUILDING_USE TableDataset BLD_BUILDING_USE #;SDEADM.BLD_BUILDING_CIVIC_LINK TableDataset BLD_BUILDING_CIVIC_LINK #;SDEADM.BLD_building_group_has_link RelationshipClass BLD_building_group_has_link #;SDEADM.BLD_BUILDING_GROUP TableDataset BLD_BUILDING_GROUP #;LND_land_assetcode 'CV domain' LND_land_assetcode #;AAA_asset_owner 'CV domain' AAA_asset_owner #;AAA_asset_locgen 'CV domain' AAA_asset_locgen #;AAA_yes_no 'CV domain' AAA_yes_no #;AAA_asset_conf 'CV domain' AAA_asset_conf #;LND_modified_type 'CV domain' LND_modified_type #;AAA_asset_group 'CV domain' AAA_asset_group #;AAA_asset_stat 'CV domain' AAA_asset_stat #;AAA_asset_crit 'CV domain' AAA_asset_crit #;AAA_asset_performrat 'CV domain' AAA_asset_performrat #;AAA_asset_condrat 'CV domain' AAA_asset_condrat #;AAA_operator_asset 'CV domain' AAA_operator_asset #;LND_land_source 'CV domain' LND_land_source #;SourceAccuracy 'CV domain' SourceAccuracy #;Bldg_Official_Name 'CV domain' Bldg_Official_Name #;LND_land_park_maint 'CV domain' LND_land_park_maint #;LND_land_park_type 'CV domain' LND_land_park_type #;LND_land_class 'CV domain' LND_land_class #;LND_land_asset_type 'CV domain' LND_land_asset_type #;LND_land_serv_cat 'CV domain' LND_land_serv_cat #;LND_land_acq_type 'CV domain' LND_land_acq_type #;LND_land_acq_purp 'CV domain' LND_land_acq_purp #;AAA_hrm_dept 'CV domain' AAA_hrm_dept #;AAA_asset_trans_type 'CV domain' AAA_asset_trans_type #;LND_land_disp_type 'CV domain' LND_land_disp_type #;Bldg_TBL_source 'CV domain' Bldg_TBL_source #;Bldg_nbc_part 'CV domain' Bldg_nbc_part #;Bldg_fsa_code 'CV domain' Bldg_fsa_code #;Bldg_alarm_sprinkler_system 'CV domain' Bldg_alarm_sprinkler_system #;Bldg_structure_type 'CV domain' Bldg_structure_type_1 #;Bldg_construction_type 'CV domain' Bldg_construction_type #;Bldg_fcode 'CV domain' Bldg_fcode #;Bldg_FC_source 'CV domain' Bldg_FC_source #;Bldg_symbol_fcode 'CV domain' Bldg_symbol_fcode #;Bldg_BLIS_uses 'CV domain' Bldg_BLIS_uses #;Bldg_occclass 'CV domain' Bldg_occclass #;Bldg_BLRC_uses 'CV domain' Bldg_BLRC_uses #;Bldg_BLTR_uses 'CV domain' Bldg_BLTR_uses #;Bldg_BLRS_uses 'CV domain' Bldg_BLRS_uses #;Bldg_BLCM_uses 'CV domain' Bldg_BLCM_uses #;Bldg_BLID_uses 'CV domain' Bldg_BLID_uses #;Bldg_BLAF_uses 'CV domain' Bldg_BLAF_uses #;Bldg_BLIT_uses 'CV domain' Bldg_BLIT_uses #"
    # )


def import_feature(feature, workspace):
    # arcpy.conversion.FeatureClassToFeatureClass(
    #     r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study",
    #     r"T:\work\giss\monthly\202208aug\gallaga\Traffic Study Schema\scripts\sys_admin-main (1)\sys_admin-main\scratch.gdb",
    #     "TRN_traffic_study", '',
    #     r'TRFSDYID "TrafficStudyID" false true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,TRFSDYID,0,50;REQ_NUM "Request Number" true true false 25 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,REQ_NUM,0,25;STUDY_TYPE "Traffic Study Type" true true false 4 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STUDY_TYPE,0,4;FILE_NAME "Associated File" true true false 255 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,FILE_NAME,0,255;STREETNAME1 "Main Street Name" true true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STREETNAME1,0,50;STREETNAME2 "Street Name 2" true true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STREETNAME2,0,50;STREETNAME3 "Street Name 3" true true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STREETNAME3,0,50;STREETNAME4 "Street Name 4" true true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STREETNAME4,0,50;STREETNAME5 "Street Name 5" true true false 50 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,STREETNAME5,0,50;FULL_CIVIC "Civic Address" true true false 60 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,FULL_CIVIC,0,60;SURVEYDATE1 "Start Date" true true false 8 Date 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,SURVEYDATE1,-1,-1;SURVEYDATE2 "Finish Date" true true false 8 Date 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,SURVEYDATE2,-1,-1;YEAR "Year" true true false 2 Short 0 5,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,YEAR,-1,-1;EQUIP_TYPE "Equipment Type" true true false 10 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,EQUIP_TYPE,0,10;COMMENT_BOX "Comments" true true false 200 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,COMMENT_BOX,0,200;DAY_WEEK1 "Start Day of Week" true true false 5 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,DAY_WEEK1,0,5;DAY_WEEK2 "Finish Day of Week" true true false 5 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,DAY_WEEK2,0,5;WEATHER "Weather Conditions" true true false 5 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,WEATHER,0,5;DIR_FROM "Direction From" true true false 2 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,DIR_FROM,0,2;DIR_TO "Direction To" true true false 2 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,DIR_TO,0,2;TIME_AM "AM Peak" true true false 1 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,TIME_AM,0,1;TIME_PM "PM Peak" true true false 1 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,TIME_PM,0,1;TIME_OP "Off Peak" true true false 1 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,TIME_OP,0,1;TIME_DAY "Duration" true true false 10 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,TIME_DAY,0,10;F85TH_PER "85th Percentile Speed" true true false 2 Short 0 5,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,F85TH_PER,-1,-1;WNT_PTS "Warrant Points" true true false 2 Short 0 5,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,WNT_PTS,-1,-1;OBSV_TYPE "Observation Type" true true false 30 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,OBSV_TYPE,0,30;ADDBY "Add By" false true false 32 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,ADDBY,0,32;ADDDATE "Add Date" false true false 8 Date 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,ADDDATE,-1,-1;MODBY "Modified By" false true false 32 Text 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,MODBY,0,32;MODDATE "Modified Date" false true false 8 Date 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,MODDATE,-1,-1;GLOBALID "GLOBALID" false false true 38 GlobalID 0 0,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,GLOBALID,-1,-1;AAWT "AAWT" true true false 4 Long 0 5,First,#,C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde\SDEADM.TRN_traffic_study,AAWT,-1,-1',
    #     '')
    pass


if __name__ == "__main__":
    trn_bridge = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_RW_SDE.sde\SDEADM.TRN_bridge"

    workspace = create_fgdb(out_folder_path=r"T:\work\giss\monthly\202208aug\gallaga\TRN_Bridge\scripts")
    print(workspace)

    local_bridge = copy_feature(trn_bridge, workspace)
    print(local_bridge)
