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
    print(f"\tFile Geodatabase {out_name} created in {out_folder_path}!")

    return fgdb


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
