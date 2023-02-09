import arcpy
import os
import logging
import functools


def with_msgs(command):
    print('-' * 100)
    command
    print(arcpy.GetMessages(0))
    print('-' * 100)
    
    
def arcpy_messages(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            messages = arcpy.GetMessages()
            message_lines = messages.split("\n")

            for message in message_lines:
                if message:
                    print(f"\t{message}")

            return result

        except arcpy.ExecuteError as e:
            print(f"ARCPY ERROR: {e}")

    return wrapper


def create_fgdb(out_folder_path: str = os.getcwd(), out_name: str = "scratch.gdb") -> str:
    """
    Creates a file geodatabase (fgdb) in the specified output folder.

    :param out_folder_path: The path to the folder where the fgdb should be
    :param out_name: The name for the fgdb. Default is "scratch.gdb".
    :return: The path to the file geodatabase.
    """

    print(f"\nCreating File Geodatabase '{out_name}'...")
    workspace_path = os.path.join(out_folder_path, out_name)

    if arcpy.Exists(workspace_path):
        print(f"\tFile Geodatabase already exists!")
        return workspace_path

    fgdb = arcpy.CreateFileGDB_management(out_folder_path, out_name).getOutput(0)
    print(f"\tFile Geodatabase {out_name} created in {out_folder_path}!")

    return fgdb


def setupLog(log_file, log_to_console: bool = False):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s: %(message)s', datefmt='%m-%d-%Y %H:%M:%S')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    trn_bridge = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_RW_SDE.sde\SDEADM.TRN_bridge"

    workspace = create_fgdb(out_folder_path=r"T:\work\giss\monthly\202208aug\gallaga\TRN_Bridge\scripts")
    print(workspace)

    local_bridge = copy_feature(trn_bridge, workspace)
    print(local_bridge)
