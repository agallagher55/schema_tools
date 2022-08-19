import arcpy


def turn_on_editor_tracking(feature):
    print(f"\nTurning ON Editor Tracking for feature: {feature}...")

    arcpy.EnableEditorTracking_management(
        in_dataset=feature,
        creator_field="ADDBY",
        creation_date_field="ADDDATE",
        last_editor_field="MODBY",
        last_edit_date_field="MODDATE",
        add_fields="NO_ADD_FIELDS",  # NO_ADD_FIELDS, ADD_FIELDS
        record_dates_in="DATABASE_TIME"  # UTC, DATABASE_TIME
    )


def turn_off_editor_tracking(feature):
    print(f"\nTurning OFF Editor Tracking for feature: {feature}...")

    arcpy.DisableEditorTracking_management(in_dataset=feature)


if __name__ == "__main__":
    import os

    import utils

    trn_bridge_sde = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_RW_SDE.sde\SDEADM.TRN_bridge"

    workspace = utils.create_fgdb(out_folder_path=r"T:\work\giss\monthly\202208aug\gallaga\TRN_Bridge\scripts")

    local_trn_bridge = os.path.join(workspace, "TRN_bridge")

    turn_on_editor_tracking(local_trn_bridge)
    # turn_off_editor_tracking(local_trn_bridge)


