import os
import arcpy

import connections
import attribute_rules
import utils

from configparser import ConfigParser

from domains import transfer_domains, domains_in_db

from SpatialDataSubmissionForms.features import Feature
from SpatialDataSubmissionForms.reporter import FieldsReport, DomainsReport

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

READY_TO_ADD_TO_REPLICA = False

# SDE = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\PROD_RW_SDEADM.sde"
SDE = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"

SPATIAL_REFERENCE = os.path.join(SDE, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

USER_PRIVILEGE = "PUBLIC"
VIEW_PRIVILEGE = "GRANT"

IMMUTABLE_FIELDS = {
    "OBJECTID", "GLOBALID", "ADDBY", "ADDDATE",
    "MODBY", "MODDATE", "SHAPE", "SHAPE_AREA", "SHAPE_LENGTH"
}


if __name__ == "__main__":
    sdsf = r"T:\work\giss\monthly\202212dec\gallaga\Traffic Calming Assessment\scripts\TCA_DataRequest.xlsx"
    sheet_name = "DATASET DETAILS"

    unique_id_fields = {
        'TRN_traffic_calming_assessment': {
            "field": "TRFSPDID",
            "prefix": "TRFSPD"
        },

    }
    
    subtype_domain_field = "VENDLOC"
    SUBTYPE_DOMAINS = {
        "field": "VENDLOC",
        "domains": [
            {"code": 1, "domain": "LND_vendor_location_food_truck"},
            {"code": 2, "domain": "LND_vendor_location_food_stand"},
            {"code": 3, "domain": "LND_vendor_location_artisan"}
        ]
    }

    CURRENT_DIR = os.getcwd()

    local_gdb = utils.create_fgdb(out_folder_path=CURRENT_DIR, out_name="scratch.gdb")

    for dbs in [
        # [local_gdb],
        # connections.dev_connections,
        [config.get("SERVER", "dev_rw")],
        # connections.qa_connections,
        # connections.prod_connections
    ]:
        for count, db in enumerate(dbs, start=1):
            print(f"\n{count}/{len(dbs)}) Database: {db}")

            # Determine the type and read-write status of a database. Ex) SDE + RW, SDE + RO, GDB, etc.
            db_type, db_rights = connections.connection_type(db)

            for xl_file in [
                sdsf,
            ]:
                print(f"\nCreating feature from {xl_file}...")
                fields_report = FieldsReport(xl_file)

                feature_name = fields_report.feature_class_name  # Should be all lower case except for the prefix
                feature_shape = fields_report.feature_shape

                if feature_shape == "Line":
                    feature_shape = "Polyline"

                field_data = fields_report.field_details

                domains_report = DomainsReport(xl_file)
                domains = domains_report.domain_names

                # Append any LONG, additional, pre-existing domains not outlined in the SDSF here.
                # domains.append("TRN_StreetName")  # Manually add TRN_StreetName domain

                domain_info = domains_report.domain_data

                if db_type == "GDB":

                    # Transfer existing domains to local dgb and find new domains not in SDE
                    new_domains = transfer_domains(
                        domains=domains,
                        output_workspace=db,
                        from_workspace=SDE
                    ).get("unfound_domains")

                else:
                    # Check for new domains not found in sde
                    domains_in_sde, new_domains = domains_in_db(db, domains)

                # Create any new domains
                if new_domains:
                    print(f"\nNew domains to create: {', '.join(new_domains)}")

                    for domain in new_domains:
                        try:
                            field_type = "TEXT"
                            
                            # Check if domain is a subtype domain
                            if SUBTYPE_DOMAINS:
                                if domain in [d["domain"] for d in SUBTYPE_DOMAINS["domains"]]:
                                    field_type = "LONG"
                                    print("\t*Subtype Domain Found!")

                            print(f"\n\tCreating domain '{domain}'...")
                            arcpy.arcpy.CreateDomain_management(
                                in_workspace=db,
                                domain_name=domain,
                                field_type=field_type,
                                domain_type="CODED",
                                domain_description=""
                            )
                            # Sometimes this says it 'fails', but domain still gets created

                        except arcpy.ExecuteError:
                            arcpy_msg = arcpy.GetMessages(2)
                            print(f"Arcpy Error: {arcpy_msg}")
                            print(f"^^^*(Sometimes this fails in the script, but domain still gets created.)")

                        domain_info = domains_report.domain_data.get(domain)

                        # Populate new domains with codes and values:
                        # Sort new domains by domain values
                        # for row in domain_info.itertuples():
                        for row in sorted([x for x in domain_info.itertuples()], key=lambda x: x.Description):
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

                # If workspace is RW and NOT RO, create the feature and add fields
                if (db_type == "SDE" and db_rights == "RW") or (db_type == "GDB" and not db_rights):

                    # Create feature (uses feature class to feature class
                    new_feature = Feature(
                        workspace=db,
                        feature_name=feature_name,
                        geometry_type=feature_shape,
                        spatial_reference=SPATIAL_REFERENCE
                    )

                    print("\nAdding Fields...")
                    feature_fields = field_data["Field Name"].values

                    for row_num, row in field_data.iterrows():

                        field_name = row["Field Name"].upper().strip()
                        field_length = row["Field Length (# of characters)"]

                        if field_name not in IMMUTABLE_FIELDS:

                            if field_length:
                                field_length = int(field_length)

                            if not field_length and not field_type != "TEXT":
                                raise ValueError(f"Field of type {field_type} needs to have a field length.")

                            alias = row["Alias"]
                            field_type = row["Field Type"]
                            field_len = field_length
                            nullable = row["Nullable"]
                            default_value = row["Default Value"]
                            domain = row["Domain"] or "#"

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

                    # TODO: Copy from RW into RO instead of re-creating feature
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
                    if feature_name in unique_id_fields:

                        id_field = unique_id_fields.get(feature_name).get("field")
                        prefix = unique_id_fields.get(feature_name).get("prefix")

                        print(f"Creating Sequence and Attribute Rule for {id_field} with prefix {prefix}...")

                        attribute_rules.add_sequence_rule(
                            workspace=db,
                            feature_name=new_feature.feature,
                            field_name=id_field,
                            sequence_prefix=prefix
                        )

                        print(f"\nAdding attribute index on {id_field}...")
                        # TODO: only add index AFTER feature has been added to Read-only and add to replica
                        try:
                            arcpy.AddIndex_management(
                                in_table=new_feature.feature,
                                fields=id_field,
                                index_name="unique_id",
                                unique="UNIQUE",
                                ascending="ASCENDING"
                            )

                        except arcpy.ExecuteError:
                            arcpy_msg = arcpy.GetMessages(2)
                            print(arcpy_msg)


# TODO: Unable to add features to replica (RO)
# TODO: Add to WGS84 script once in prod. (DC1-GIS-APP-P22)
