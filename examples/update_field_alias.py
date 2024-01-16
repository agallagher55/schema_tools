"""
Date:
"""

import arcpy
import os
import sys
import datetime
import time
import traceback
import logging

from configparser import ConfigParser

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

# Config Parser
config = ConfigParser()
config.read("E:\\HRM\\Scripts\\Python\\config.ini")

script_config = ConfigParser()
script_config.read('config.ini')

# Logging
log_dir = config.get('LOGGING', 'logDir')
log_dir = os.getcwd()

# File handler
logFile = log_dir + "\\script_logs.log"
file_handler = logging.FileHandler(logFile)

# Console handler
console_handler = logging.StreamHandler()

# Configure formatter
log_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | FUNCTION: %(funcName)s | Msgs: %(message)s', datefmt='%d-%b-%y %H:%M:%S'
)
file_handler.setFormatter(log_formatter)
console_handler.setFormatter(log_formatter)

# Set logging level
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)

# Create logger and add handlers
logger = logging.getLogger('')
logger.addHandler(file_handler)  # Write logs to a file
logger.addHandler(console_handler)  # logger.info logs to the console

# VARIABLES


# Functions
def update_field_alias(feature, field, field_alias):
    print(f"\nUpdating field '{field}' in feature '{feature}' to alias '{field_alias}'...")
    arcpy.AlterField_management(
        in_table=feature,
        field=field,
        # new_field_name=None,
        new_field_alias=field_alias,
        # field_type=None,
        # field_length=None,
        # field_is_nullable=None,
        # clear_field_alias=None
    )


if __name__ == "__main__":

    startTime = time.asctime(time.localtime(time.time()))
    logger.info("Start: " + startTime)
    logger.info("-----------------------")

    PC_NAME = os.environ['COMPUTERNAME']
    run_from = "SERVER" if "APP" in PC_NAME else "LOCAL"

    print(f"\nPC Name: {PC_NAME}\n\tRunning from: {run_from}...")

    try:

        for dbs in [
            # [
            #     script_config.get("SERVER", "qa_rw"),
            #     script_config.get("SERVER", "qa_ro"),
            #     script_config.get("SERVER", "qa_web_ro"),
            #     script_config.get("SERVER", "qa_web_ro_gdb"),
            # ],
            [
                script_config.get("SERVER", "prod_rw"),
                script_config.get("SERVER", "prod_ro"),
                script_config.get("SERVER", "prod_ro_web"),
                script_config.get("SERVER", "prod_web_ro_gdb"),
            ],
        ]:
            if dbs:
                print(f"\nProcessing dbs: {', '.join(dbs)}...")

                for db in dbs:
                    print(f"\nDATABASE: {db}")

                    # SDE = r"E:\HRM\Scripts\SDE\SQL\qa_RW_sdeadm.sde"
                    update_feature = "SDEADM.ADM_growth_control_area"
                    if db.upper().endswith("GDB"):
                        update_feature = update_feature.upper().replace("SDEADM.", "")

                    with arcpy.EnvManager(workspace=db):
                        update_field_alias(
                            feature=update_feature,
                            field="GSA_NAME",
                            field_alias='Community'
                        )
                        print(arcpy.GetMessages())

    except arcpy.ExecuteError:
        arcpy_msg = arcpy.GetMessages(2)
        logger.error(arcpy_msg)

    except Exception as e:
        print(e)

        # Return any python specific errors as well as any errors from the geoprocessor
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
        logger.error(pymsg)

        msgs = "GP ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        logger.error(msgs)

        # send_error("ERROR - BUILDING PERMIT ERROR", "DC1-GIS-APP-Q203 / BuildingPermits.py")

        sys.exit()

    # Close the Log File:
    endTime = time.asctime(time.localtime(time.time()))
    logger.info("-----------------------")
    logger.info("End: " + endTime)
