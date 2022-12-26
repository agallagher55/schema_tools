import os
import arcpy

import connections
import attribute_rules
import utils

from domains import transfer_domains, domains_in_db

from SpatialDataSubmissionForms.features import Feature
from SpatialDataSubmissionForms.reporter import FieldsReport, DomainsReport

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

READY_TO_ADD_TO_REPLICA = False

# SDE_PROD_RW = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\PROD_RW_SDEADM.sde"
SDE_PROD_RW = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"

SPATIAL_REFERENCE = os.path.join(SDE_PROD_RW, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

USER_PRIVILEGE = "PUBLIC"
VIEW_PRIVILEGE = "GRANT"


if __name__ == "__main__":
    traffic_calming_info_xl = r"T:\work\giss\monthly\202212dec\gallaga\Trafic Calming Assessment\scripts\TCA_DataRequest.xlsx"

    sheet_name = "DATASET DETAILS"

    AUTO_INC_IDS = {
        'TRN_Traffic_Calming_Assessment': {
            "field": "TRFSPDID",
            "prefix": "TRFSPD"
        },

    }

    CURRENT_DIR = os.getcwd()

    local_gdb = utils.create_fgdb(out_folder_path=CURRENT_DIR, out_name="scratch.gdb")

    for dbs in [
        [local_gdb]
        # connections.dev_connections,
        # connections.qa_connections,
        # connections.prod_connections
    ]:
        for count, db in enumerate(dbs, start=1):
            print(f"\n{count}/{len(dbs)}) Database: {db}")

            db_type, db_rights = connections.connection_type(db)

            for xl_file in [
                traffic_calming_info_xl,
            ]:
                print(f"\nCreating feature from {xl_file}...")
                fields_report = FieldsReport(xl_file)

                feature_name = fields_report.feature_class_name
                feature_shape = fields_report.feature_shape
                if feature_shape == "Line":
                    feature_shape = "Polyline"

                field_data = fields_report.field_details

                domains_report = DomainsReport(xl_file)
                domains = domains_report.domain_names

                # Append any LONG, additional, pre-existing domains not outlined in the SPSF here.
                # domains.append("TRN_StreetName")  # Manually add TRN_StreetName domain

                domain_info = domains_report.domain_data

                # if scratch_gdb or ro_gdb:
                if db_type == "GDB":

                    # Transfer existing domains to local dgb and find new domains not in SDE
                    new_domains = transfer_domains(
                        domains=domains,
                        output_workspace=db,
                        from_workspace=SDE_PROD_RW).get("unfound_domains")

                else:
                    # Check for new domains not found in sde
                    domains_in_sde, new_domains = domains_in_db(db, domains)

                # Create any new domains
                if new_domains:
                    print(f"\nNew domains to create: {', '.join(new_domains)}")

                    for domain in new_domains:
                        try:
                            print(f"\tCreating domain '{domain}'...")
                            arcpy.management.CreateDomain(
                                in_workspace=db,
                                domain_name=domain,
                                field_type="TEXT",
                                domain_type="CODED",
                                domain_description=""
                            )
                            # Sometimes this says it 'fails', but domain still gets created

                        except arcpy.ExecuteError as e:
                            print(f"Arcpy Error: {e}")
                            print(f"^^^*(Sometimes this fails in the script, but domain still gets created.)")

                        # Add code, values
                        domain_info = domains_report.domain_data.get(domain)

                        # for code, value in domain_info.items():
                        for row in domain_info.itertuples():
                            code = row.Code
                            desc = row.Description

                            print(f"\tAdding ({code}: {desc})")
                            arcpy.management.AddCodedValueToDomain(
                                in_workspace=db,
                                domain_name=domain,
                                code=code,
                                code_description=desc
                            )
                else:
                    print("\nNO new domains to create.")

                # If workspace is RW and NOT RO
                if (db_type == "SDE" and db_rights == "RW") or (db_type == "GDB" and not db_rights):

                    # Create feature
                    new_feature = Feature(
                        workspace=db,
                        feature_name=feature_name,
                        geometry_type=feature_shape,
                        spatial_reference=SPATIAL_REFERENCE
                    )

                    # ADD FIELDS, applying domain if applicable
                    print("\nAdding Fields...")

                    ignore_fields = {
                        "OBJECTID", "GLOBALID", "ADDBY", "ADDDATE",
                        "MODBY", "MODDATE", "SHAPE", "SHAPE_AREA", "SHAPE_LENGTH"
                    }
                    feature_fields = field_data["Field Name"].values

                    for row_num, row in field_data.iterrows():  # TODO: shape area, shape length fields is appearing first

                        field_name = row["Field Name"].upper().strip()
                        field_length = row["Field Length (# of characters)"]

                        if field_name not in ignore_fields:

                            if field_length:
                                field_length = int(field_length)

                            if not field_length and not field_type != "TEXT":
                                raise ValueError(f"Field of type {field_type} needs to have a field length.")

                            alias = row["Alias"]
                            field_type = row["Field Type"]
                            field_len = field_length
                            # nullable = row["Nullable"] or "NON_NULLABLE"
                            nullable = row["Nullable"]
                            default_value = row["Default Value"]
                            domain = row["Domain"] or "#"
                            notes = row["Notes"]

                            new_feature.add_field(
                                field_name=field_name.upper(),
                                field_type=field_type,
                                length=field_len,
                                alias=alias,
                                nullable=nullable,
                                domain_name=domain
                            )

                            if domain and domain != "#":
                                print(f"\t\t{field_name} has domain: '{domain}'")
                                new_feature.assign_domain(
                                    field_name=field_name,
                                    domain_name=domain
                                )

                            # Apply default values for fields, if applicable
                            if default_value:
                                new_feature.add_field_default(
                                    field=field_name,
                                    value=default_value
                                )

                    # ADD GLOBAL IDS
                    new_feature.add_gloablids()

                    # ADD EDITOR TRACKING FIELDS
                    new_feature.add_editor_tracking_fields()

                    if db_type == "SDE" and db_rights == "RW":

                        if READY_TO_ADD_TO_REPLICA:
                            # Register as Versioned
                            new_feature.register_as_versioned()

                            # Copy RW feature to RO
                            ro_sde_db = db.replace("RW", "RO")
                            ro_exists = arcpy.Exists(ro_sde_db)

                            # TODO: Do we need to copy to web_ro.gdb ? Or only if, and when, we need to publish service?
                            ro_feature = os.path.join(ro_sde_db, new_feature.feature)
                            if not arcpy.Exists(ro_feature):
                                print("\tCopying RW feature to RO db...")
                                ro_feature = arcpy.CopyFeatures_management(
                                    in_features=new_feature.feature,
                                    out_feature_class=os.path.join(ro_sde_db, feature_name)
                                )[0]

                                # ro_feature = arcpy.FeatureClassToFeatureClass_conversion(
                                #     in_features=new_feature.feature,
                                #     out_path=ro_sde_db,
                                #     out_name=feature_name
                                # )[0]

                            # TODO: PAUSE & add feature to existing replica using COMMAND LINE SCRIPT

                            # T:\work\giss\tools\ModifyReplica
                            # - May have to alter command if feature is a table
                            # "C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\DEV_RO_SDEADM.sde"
                            # a) ModifyReplica.exe -w C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\DEV_RO_SDEADM.sde -r SDEADM.LND_Rosde -d SDEADM.LND_charge_areas
                            # b) ModifyReplica.exe -w C:\Workspace\Release\10_4\sdeadm_PROD_GIS_HRM_RW_Win.sde -r SDEADM.LND_Rosde -d SDEADM.LND_charge_areas

                            # input("\nAdd feature to existing replica using COMMAND LINE SCRIPT\n")

                            # TODO: Un-version RO feature. Feature is un-versioned when copied over, but adding to replica versions the feature
                            print("\tRegistering RO feature as UN-versioned...")
                            arcpy.UnregisterAsVersioned_management(in_dataset=ro_feature)

                            # TODO: Do NOT add to RW? Unsure when and how to do this
                            # TODO: SQL developer: GRANT SELECT ON SDEADM.TREEVAULTASSETID TO ATTRIBUTE_RULES_SEQ_ROLE;

                    # Update Privileges
                    new_feature.change_privileges(
                        user=USER_PRIVILEGE,
                        view=VIEW_PRIVILEGE
                    )

                    # ENABLE EDITOR TRACKING
                    new_feature.enable_editor_tracking()

                    # Attribute Rules - Add after feature has been copied to Read-Only. RW and .gdb only
                    # TODO: Add spot in excel sheet to flag unique, auto-incrementing IDs
                    # TODO: Get field name for Charge Area unique id field

                    if feature_name in AUTO_INC_IDS:
                        print(f"Adding Attribute Rule to {feature_name}...")

                        id_field = AUTO_INC_IDS.get(feature_name).get("field")
                        prefix = AUTO_INC_IDS.get(feature_name).get("prefix")

                        attribute_rules.add_sequence_rule(
                            workspace=db,
                            feature_name=new_feature.feature,
                            field_name=id_field,
                            sequence_prefix=prefix
                        )


# TODO: Unable to add features to replica (RO)
# TODO: Add to WGS84 script once in prod. (DC1-GIS-APP-P22)

# TODO: TRN_StreetName domain wasn't carried over
# TODO: Needs the unique id sequence applied
