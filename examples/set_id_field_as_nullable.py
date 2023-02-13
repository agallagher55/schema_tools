"""
To alter a field to be NULLABLE:
    - Field cannot have an attribute rule
    - If the table is not empty, the feature must not be versioned
"""

import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

"""
You edit the sequence and update the Starting value. 
when you modify (edit) a Sequence, it is dropped and recreated. 
After you edit the seq, you will also have to add the seq back to the Attribute_rules_seq_role
"""


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


def reset_sequences(workspace, sequences):
    print(f"Resetting sequences {', '.join(sequences)}...")

    # TODO: Check if field participates in an attribute rule, if so, reset the sequence for that attribute rule

    for sequence in sequences:

        try:
            arcpy.DeleteDatabaseSequence_management(in_workspace=db, seq_name=sequence)

            print(f"\tCreating db sequence {sequence}...")
            arcpy.CreateDatabaseSequence_management(
                in_workspace=workspace,
                seq_name=sequence,
                seq_start_id=1,
                seq_inc_value=1
            )

        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))

    return True


if __name__ == "__main__":
    # TODO: Update PEDRAMP ASSETID attribute rule to use PEDRMPASSETID

    FEATURE = "SDEADM.AST_PED_RAMP"
    # FEATURE = "SDEADM.LND_Charge_Areas"
    # FEATURE = "SDEADM.LND_beach_mobility"

    # NULLABLE_FIELDS = ["PEDRMPID", "ASSETID"]
    NULLABLE_FIELDS = ["PEDRMPID", "ASSETID", "ASSETCODE", "OWNER", "LOCGEN"]
    # NULLABLE_FIELDS = ["CHGAREA_ID"]
    # NULLABLE_FIELDS = ["MOBILITYID"]

    # LND_subdiv_applications (fix field aliases as well), LND_special_planning_areas

    dev_rw = r"E:\HRM\Scripts\SDE\dev_RW_sdeadm.sde"
    qa_rw = r"E:\HRM\Scripts\SDE\qa_RW_sdeadm.sde"
    prod_rw = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"

    LOCAL_GDB = create_fgdb()

    for db in [
        # dev_rw,
        # qa_rw,
        prod_rw
    ]:

        with arcpy.EnvManager(workspace=db):
            print(f"\nSDE: {db}")

            feature_name = os.path.basename(FEATURE).replace("SDEADM.", "")
            initial_feature_row_count = int(arcpy.GetCount_management(FEATURE)[0])

            backup_feature = os.path.join(LOCAL_GDB, feature_name)

            print(f"Initial row count: {initial_feature_row_count}")

            if initial_feature_row_count > 0:

                print("Backing up feature...")
                backup_feature = arcpy.FeatureClassToFeatureClass_conversion(
                    in_features=FEATURE,
                    out_path=LOCAL_GDB,
                    out_name=feature_name,
                )[0]

                # STOP associated services

                # Reset sequences for both ID fields
                # TODO: Only use fields that partake in an attribute rule
                # TODO: Will only be reached if attribute rules haven't already been deleted...

                print("Truncating table...")
                try:
                    arcpy.TruncateTable_management(FEATURE)

                except arcpy.ExecuteError:
                    print(arcpy.GetMessages(2))

                    print("\tTruncating table with update cursor...")
                    edit = arcpy.da.Editor(db)
                    edit.startEditing(True, True)
                    edit.startOperation()

                    with arcpy.da.UpdateCursor(FEATURE, "*") as cursor:
                        for row in cursor:
                            cursor.deleteRow()

                    edit.startOperation()
                    edit.stopEditing(True)

                    arcpy.ClearWorkspaceCache_management()
                    del edit

            attribute_rules = arcpy.Describe(FEATURE).attributeRules
            at_rule_fields = [x.fieldName for x in attribute_rules]
            at_rule_sequences = []

            for rule in attribute_rules:
                if "Generate ID" in rule.description:
                    sequence = rule.scriptExpression.split("NextSequenceValue")[1].split(".")[1].strip(")'")
                    at_rule_sequences.append(sequence)

            # reset_sequences(db, NULLABLE_FIELDS)
            if at_rule_sequences:
                reset_sequences(db, at_rule_sequences)

            if len(attribute_rules) > 0:  # TODO: check to see if nullable field participates in an attribute rule
                attribute_rule_export = arcpy.ExportAttributeRules_management(
                    in_table=FEATURE,
                    out_csv_file=f"../attribute_rules/{os.path.basename(FEATURE)}_attributeRules.csv"
                )[0]

                rule_names = [x.name for x in attribute_rules]
                print(f"Deleting Attribute Rules:")
                for rule in rule_names:
                    print(f"\t{rule}")

                arcpy.DeleteAttributeRule_management(FEATURE, rule_names)

            # arcpy.ReconcileVersions_management()
            print("Unregistering as versioned...")  # Often (always?) have to do this manually
            input("Unregister as versioned and then restart script to continue.")
            arcpy.UnregisterAsVersioned_management(
                in_dataset=FEATURE, keep_edit="KEEP_EDIT", compress_default="COMPRESS_DEFAULT"
            )

            # Make fields nullable
            for field in NULLABLE_FIELDS:
                # Input table must be empty in order to set field as nullable
                print(f"Altering field '{field}' to set as NULLABLE...")

                try:
                    arcpy.AlterField_management(
                        in_table=FEATURE,
                        field=field,
                        field_is_nullable="NULLABLE"
                    )

                except arcpy.ExecuteError:
                    print(arcpy.GetMessages(2))

            print("Registering as versioned...")
            arcpy.RegisterAsVersioned_management(in_dataset=FEATURE)

            # Add attribute rules back in. There should always be attribute rules for these sequences
            print("Re-applying attribute rules...")
            arcpy.ImportAttributeRules_management(
                target_table=FEATURE,
                csv_file=attribute_rule_export
            )

            print("Disabling Editor Tracking...")
            arcpy.DisableEditorTracking_management(in_dataset=FEATURE)

            print("Appending data back in...")
            arcpy.Append_management(
                inputs=backup_feature,
                target=FEATURE,
            )

            print("Re-enabling Editor Tracking...")
            arcpy.EnableEditorTracking_management(
                    in_dataset=FEATURE,
                    creator_field="ADDBY",
                    creation_date_field="ADDDATE",
                    last_editor_field="MODBY",
                    last_edit_date_field="MODDATE",
                    add_fields="NO_ADD_FIELDS",  # NO_ADD_FIELDS, ADD_FIELDS
                    record_dates_in="UTC"  # UTC, DATABASE_TIME
                )
