import os
import arcpy

import attribute_rules, connections, utils

from domains import transfer_domains

from SpatialDataSubmissionForms.features import Feature
from SpatialDataSubmissionForms.reporter import FieldsReport, DomainsReport

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

READY_TO_ADD_TO_REPLICA = False

SDE_PROD_RW = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\PROD_RW_SDEADM.sde"
SPATIAL_REFERENCE = os.path.join(SDE_PROD_RW, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

EDITOR_TRACKING_FIELD_INFO = {
    "ADDBY": {
        "field_type": "TEXT",
        "field_length": 32,
        "field_alias": "Add By"
    },
    "MODBY": {
        "field_type": "TEXT",
        "field_length": 32,
        "field_alias": "Modified By"
    },
    "ADDDATE": {
        "field_type": "DATE",
        "field_length": "",
        "field_alias": "Add Date"
    },
    "MODDATE": {
        "field_type": "DATE",
        "field_length": "",
        "field_alias": "Modified Date"
    },
}

USER_PRIVILEGE = "PUBLIC"
VIEW_PRIVILEGE = "GRANT"
EDIT_PRIVILEGE = "#"  # "GRANT"


if __name__ == "__main__":
    info_xl = r"T:\work\giss\monthly\202210oct\gallaga\Bus Shelters\Bus Shelter Point Representation Change 20Oct2022.xlsx"

    sheet_name = "DATASET DETAILS"

    AUTO_INC_IDS = {
        'TRN_transit_shelter': [
            {"field": "ASSETID", "prefix": "SHE"},
            {"field": "SHELTERID", "prefix": "SHE"}
        ]
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
                info_xl
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
                domain_info = domains_report.domain_data

                # Add domains from SDE to local gdb
                new_domains = transfer_domains(domains=domains, output_workspace=db, from_workspace=SDE_PROD_RW).get("unfound_domains")

                # Create any new domains
                if new_domains:
                    print(f"\nNew domains to create: {', '.join(new_domains)}")

                    # TODO: Get FIELD TYPE for domains
                    domain_field_types = fields_report.domain_fields()

                    for domain in new_domains:

                        try:
                            domain_field_type = "TEXT"

                            # Get domain field type
                            domain_field_info = [x for x in domain_field_types if x.get("Domain") == domain]

                            if domain_field_info:
                                domain_field_type = domain_field_info[0].get("Field Type")

                            print(f"\n\tCreating {domain_field_type} domain '{domain}'...")

                            arcpy.management.CreateDomain(
                                in_workspace=db,
                                domain_name=domain,
                                field_type=domain_field_type,
                                domain_type="CODED"
                            )
                            # Sometimes this says it 'fails', but domain still gets created

                        except arcpy.ExecuteError as e:
                            print(f"Arcpy Error: {e}")
                            print(f"^^^*(Sometimes this fails in the script, but domain still gets created.)")

                        # Add code, values
                        domain_info = domains_report.domain_data.get(domain)

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

                # ALL Workspaces

                # If workspace is RW and NOT RO
                if (db_type == "SDE" and db_rights == "RW") or (db_type == "GDB" and not db_rights):

                    # Create feature
                    new_feature = Feature(
                        workspace=db,
                        feature_name=feature_name,
                        geometry_type=feature_shape,
                        spatial_reference=SPATIAL_REFERENCE
                    )

                    # Add fields, applying domain if applicable
                    print("\nAdding Fields...")

                    ignore_fields = {
                        "OBJECTID", "GLOBALID", "ADDBY", "ADDDATE",
                        "MODBY", "MODDATE", "SHAPE", "SHAPE_AREA", "SHAPE_LENGTH"
                    }
                    feature_fields = field_data["Field Name"].values

                    for row_num, row in field_data.iterrows():  # TODO: shape area, shape length fields is appearing first (only for local geodatabase)

                        field_name = row["Field Name"].upper().strip()
                        field_length = row["Field Length (# of characters)"]
                        field_type = row["Field Type"]

                        if field_name not in ignore_fields:

                            if field_length:
                                field_length = int(field_length)

                            if not field_length and not field_type != "TEXT":
                                raise ValueError(f"Field of type {field_type} needs to have a field length.")

                            alias = row["Alias"]
                            field_type = row["Field Type"]
                            field_len = field_length
                            nullable = row["Nullable"] or "NON_NULLABLE"
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
                                print(f"\tField has domain: '{domain}'")
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

                    # Add attribute index
                    print(f"\nAdding index to 'MOBILITYID' field...")

                    # try:
                    #     arcpy.AddIndex_management(
                    #         in_table=new_feature,
                    #         fields="MOBILITYID",
                    #         index_name="MobilityID",
                    #         unique="UNIQUE"
                    #     )
                    #
                    # except arcpy.ExecuteError:
                    #     print(f"ERROR: Was unable to add attribute index.")
                    #     print(arcpy.GetMessages(2))


                    # ADD GLOBAL IDS
                    new_feature.add_gloablids()

                    # ADD EDITOR TRACKING FIELDS
                    new_feature.add_editor_tracking_fields(EDITOR_TRACKING_FIELD_INFO)

                    if db_type == "SDE" and db_rights == "RW":

                        # Register as Versioned
                        new_feature.register_as_versioned()

                        if READY_TO_ADD_TO_REPLICA:

                            # Copy RW feature to RO
                            ro_sde_db = db.replace("RW", "RO")
                            ro_feature = os.path.join(ro_sde_db, new_feature.feature)

                            # TODO: Do we need to copy to web_ro.gdb ? Or only if, and when, we need to publish service?
                            if not arcpy.Exists(ro_feature):
                                print("\tCopying RW feature to RO db...")
                                ro_feature = arcpy.CopyFeatures_management(
                                    in_features=new_feature.feature,
                                    out_feature_class=os.path.join(ro_sde_db, feature_name)
                                )[0]

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

                    # ENABLE EDITOR TRACKING - Only for RW
                    new_feature.enable_editor_tracking()

                    # Update Privileges
                    new_feature.change_privileges(
                        user=USER_PRIVILEGE,
                        view=VIEW_PRIVILEGE
                    )

                    # Attribute Rules - Add after feature has been copied to Read-Only. RW and .gdb only
                    # TODO: Add spot in excel sheet to flag unique, auto-incrementing IDs
                    # TODO: Get field name for Charge Area unique id field

                    if feature_name in AUTO_INC_IDS:
                        for field in AUTO_INC_IDS.get(feature_name):
                            id_field = field.get("field")
                            prefix = field.get("prefix")

                            attribute_rules.add_sequence_rule(
                                workspace=db,
                                feature_name=new_feature.feature,
                                field_name=id_field,
                                sequence_prefix=prefix
                            )

    """
    NOTES:
        - Unable to add features to replica (RO)
        - Add to WGS84 script once in prod. (DC1-GIS-APP-P22)
    """


