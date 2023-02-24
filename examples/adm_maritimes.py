import os
import arcpy

import replicas

dev_rw = r"E:\HRM\Scripts\SDE\dev_RW_sdeadm.sde"
dev_ro = r"E:\HRM\Scripts\SDE\dev_RO_sdeadm.sde"
dev_web_ro = r"E:\HRM\Scripts\SDE\dev_RO_webgis.sde"
dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"

qa_rw = r"E:\HRM\Scripts\SDE\qa_RW_sdeadm.sde"
qa_ro = r"E:\HRM\Scripts\SDE\qa_RO_sdeadm.sde"
qa_web_ro = r"E:\HRM\Scripts\SDE\qa_RO_webgis.sde"
qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"

prod_rw = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"
prod_ro = r"E:\HRM\Scripts\SDE\prod_RO_sdeadm.sde"
prod_web_ro = r"E:\HRM\Scripts\SDE\prod_RO_webgis.sde"
prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_PROD\fgdbs\web_RO.gdb"

features = [
    "SDEADM.ADM_maritimes",
    "SDEADM.ADM_maritimes_250k",
    # "SDEADM.ADM_maritimes_clip",  # Need to pause service to update RO maritimes_clip feature with GlobalIDs.
]


def update_features(rw_workspace=qa_rw, ro_workspace=qa_ro, ro_web_workspace=qa_web_ro, ro_web_gdb_workspace=qa_web_ro_gdb, skip_web_copy=True):

    # Delete feature from RO
    for feature in features:
        print(f"\nProcessing {feature.upper()}...")

        delete_from_workspaces = [ro_workspace, ro_web_workspace, ro_web_gdb_workspace]
        if skip_web_copy:
            delete_from_workspaces = [ro_workspace]

        for workspace in delete_from_workspaces:
            with arcpy.EnvManager(workspace=workspace):
                feature_name = feature

                if workspace == ro_web_workspace:
                    feature_name = feature_name.replace("SDEADM.", "WEBGIS.")

                elif workspace == ro_web_gdb_workspace:
                    feature_name = feature_name.replace("SDEADM.", "")

                print(f"\tDeleting {os.path.join(workspace, feature_name)}...")
                arcpy.Delete_management(feature_name)

        with arcpy.EnvManager(workspace=rw_workspace):
            # Add GlobalIDs to RW
            print(f"\n\tAdding GlobalIDs to {os.path.join(rw_workspace, feature)}...")
            arcpy.AddGlobalIDs_management(feature)

            # Copy RW feature to RO
            # for workspace in [ro_workspace, ro_web_workspace, ro_web_gdb_workspace]:

            try:

                print(f"\tCopying {os.path.join(rw_workspace, feature)} to {os.path.join(ro_workspace, feature)}...")
                ro_feature = arcpy.Copy_management(
                    in_data=feature,
                    out_data=os.path.join(ro_workspace, feature)
                )[0]

                # Grant public privilege
                print("\tGranting View privilege to PUBLIC user...")
                arcpy.ChangePrivileges_management(
                    ro_feature,
                    user="PUBLIC",
                    View="GRANT"
                )

                # Only need to copy over WEBGIS.ADM_maritimes, web_ro.gdb/ADM_maritimes
                if feature != "SDEADM.ADM_maritimes":
                    continue

                # Project RO to RO_WEBGIS
                if not skip_web_copy:
                    feature_name = feature.replace("SDEADM.", "WEBGIS.")
                    webgis_feature = os.path.join(ro_web_workspace, feature_name)
                    print(f"\n\tCopying (projecting) {ro_feature} to {webgis_feature}")
                    arcpy.Project_management(
                        ro_feature,
                        webgis_feature,
                        'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]',
                        "'NAD83_CSRS_1997_to_NAD83_CSRS_2010 + NAD_1983_CSRS_To_WGS_1984_2'",
                        'PROJCS["NAD_1983_CSRS_2010_MTM_5_Nova_Scotia",GEOGCS["GCS_North_American_1983_CSRS_2010",DATUM["D_North_American_1983_CSRS",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",25500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-64.5],PARAMETER["Scale_Factor",0.9999],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
                    )

                    # Copy WEBGIS feature to web gdb
                    feature_name = feature.replace("SDEADM.", "")
                    webgdb_feature = os.path.join(ro_web_gdb_workspace, feature_name)
                    print(f"\tCopying {webgis_feature} to {webgdb_feature}...")
                    arcpy.Copy_management(
                        in_data=webgis_feature,
                        out_data=webgdb_feature
                    )

                else:
                    print("*SKIPPING WGS84 features.")

            except arcpy.ExecuteError:
                print(arcpy.GetMessages(2))


if __name__ == "__main__":
    # TODO: Need to pause service to update RO maritimes_clip feature with GlobalIDs.
    #  HRM/Aerial_Photography_2014_2016/MapServer

    # TODO: remove lock from WEBGIS.ADM_maritimes (IMSuser)  - Update RO and see if WEBGIS.xxx updates over the weekend.

    # Deletes, and updates, RO features
    update_features(
        rw_workspace=prod_rw,
        ro_workspace=prod_ro,
        ro_web_workspace=prod_web_ro,
        ro_web_gdb_workspace=prod_web_ro_gdb,
        skip_web_copy=True
    )

    # Add features to replica
    replicas.add_to_replica(
        replica_name='ADM_Rosde',
        rw_sde=prod_rw,
        ro_sde=prod_ro,
        add_features=features,
        topology_dataset=False
    )

