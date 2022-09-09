import arcpy
import os
import logging


def with_msgs(command):
    print('-' * 100)
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)


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


def copy_feature(copy_feature, output_workspace):
    """
    - Copy Features, carrying over domains
    :param copy_feature:
    :param output_workspace:
    :return:
    """

    print(f"\nCopying '{copy_feature}' to {output_workspace}...")

    feature_name = arcpy.Describe(copy_feature).name.replace("SDEADM.", "")  # Remove SDEADM.
    output_feature = os.path.join(output_workspace, feature_name)

    with arcpy.EnvManager(workspace=output_workspace):
        workspace_features = arcpy.ListFeatureClasses()

        # Check if feature already exists in workspace
        if feature_name not in workspace_features:

            arcpy.Copy_management(
                in_data=copy_feature,
                out_data=output_feature
            )

            return output_feature

        else:
            print(f"\t*{feature_name} already exists in {output_workspace}.")


def setupLog(fileName):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s: %(message)s', datefmt='%m-%d-%Y %H:%M:%S')

    handler = logging.FileHandler(fileName)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    trn_bridge = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_RW_SDE.sde\SDEADM.TRN_bridge"

    workspace = create_fgdb(out_folder_path=r"T:\work\giss\monthly\202208aug\gallaga\TRN_Bridge\scripts")
    print(workspace)

    local_bridge = copy_feature(trn_bridge, workspace)
    print(local_bridge)
