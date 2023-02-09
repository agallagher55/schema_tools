"""
To alter a field to be NULLABLE:
- Field cannot have an attribute rule
- If the table is not empty, the feature must not be versioned
"""
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

# FEATURE = "SDEADM.AST_PED_RAMP"
# FEATURE = "SDEADM.LND_Charge_Areas"
FEATURE = "SDEADM.LND_beach_mobility"

# NULLABLE_FIELDS = ["PEDRMPID", "ASSETID"]
# NULLABLE_FIELDS = ["CHGAREA_ID"]
NULLABLE_FIELDS = ["MOBILITYID"]

# LND_Charge_Areas (CHGAREA_ID), LND_beach_mobility (MOBILITYID), LND_subdiv_applications (fix field aliases as well), LND_special_planning_areas

dev_rw = r"E:\HRM\Scripts\SDE\dev_RW_sdeadm.sde"
qa_rw = r"E:\HRM\Scripts\SDE\qa_RW_sdeadm.sde"
prod_rw = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"

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


def reset_sequences(workspace, sequence_fields):
    for sequence_field in sequence_fields:

        try:
            arcpy.DeleteDatabaseSequence_management(in_workspace=db, seq_name=sequence_field)

        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))

        print(f"\tCreating db sequence {sequence_field}...")
        arcpy.CreateDatabaseSequence_management(
            in_workspace=workspace,
            seq_name=sequence_field,
            seq_start_id=1,
            seq_inc_value=1
        )


if __name__ == "__main__":

    LOCAL_GDB = create_fgdb()

    for db in [
        dev_rw,
        # qa_rw, 
        # prod_rw
    ]:

        with arcpy.EnvManager(workspace=db):
            print(f"\nSDE: {db}")

            feature_name = os.path.basename(FEATURE).replace("SDEADM.", "")
            initial_feature_row_count = int(arcpy.GetCount_management(FEATURE)[0])
            attribute_rules = [x.name for x in arcpy.Describe(FEATURE).attributeRules]

            print(f"Initial row count: {initial_feature_row_count}")

            # arcpy.ReconcileVersions_management()
            print("Unregistering as versioned...")  # Often (always?) have to do this manually
            arcpy.UnregisterAsVersioned_management(
                in_dataset=FEATURE, keep_edit="KEEP_EDIT", compress_default="COMPRESS_DEFAULT"
            )

            if initial_feature_row_count > 0:

                print("Backing up feature")
                backup_feature = arcpy.FeatureClassToFeatureClass_conversion(
                    in_features=FEATURE,
                    out_path=LOCAL_GDB,
                    out_name=feature_name,
                )[0]

                # Stop associated services

                # Reset sequences for both ID fields
                reset_sequences(db, NULLABLE_FIELDS)

                # print("Truncating table...")
                # try:
                #     arcpy.TruncateTable_management(FEATURE)
                #
                # except arcpy.ExecuteError:
                #     print(arcpy.GetMessages(2))
                #     edit = arcpy.da.Editor(db)
                #     edit.startEditing(True, True)
                #     edit.startOperation()
                #
                #     with arcpy.da.UpdateCursor(FEATURE, "*") as cursor:
                #         for row in cursor:
                #             cursor.deleteRow(row)
                #             print("\tRow deleted.")
                #
                #     edit.startOperation()
                #     edit.stopEditing(True)
                #
                #     arcpy.ClearWorkspaceCache_management()
                #     del edit

            if len(attribute_rules) > 0:
                attribute_rule_export = arcpy.ExportAttributeRules_management(
                    in_table=FEATURE,
                    out_csv_file=f"../attribute_rules/{os.path.basename(FEATURE)}_attributeRules.csv"
                )[0]

                print(f"Deleting Attribute Rules: {', '.join(attribute_rules)}...")
                arcpy.DeleteAttributeRule_management(FEATURE, attribute_rules)

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
            if len(attribute_rules) > 0:
                print("Re-applying attribute rules...")
                arcpy.ImportAttributeRules_management(
                    target_table=FEATURE,
                    csv_file=attribute_rule_export
                )

            if initial_feature_row_count > 0:
                print("Appending data back in...")
                arcpy.Append_management(
                    inputs=backup_feature,
                    target=FEATURE,
                )
