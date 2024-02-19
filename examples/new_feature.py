import os
import arcpy

from gispy import (
    connections,
    attribute_rules,
    utils,
)

from gispy.replicas import replicas

from configparser import ConfigParser

from gispy.subtypes import create_subtype
from gispy.domains import transfer_domains, domains_in_db

from gispy.SpatialDataSubmissionForms.features import Feature
from gispy.SpatialDataSubmissionForms.reporter import FieldsReport, DomainsReport

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

MAX_TABLE_NAME_LENGTH = 27

config = ConfigParser()
config.read('config.ini')

SDE = config.get("LOCAL", "prod_rw")

if "GIS" in os.environ.get("COMPUTERNAME").upper():
    SDE = config.get("SERVER", "prod_rw")

SPATIAL_REFERENCE = os.path.join(SDE, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

EDIT_PERMISSIONS_USERS = [
    "HRM\\GIS_TRAFFIC_EDITOR",
]

SDSF_IGNORE_FIELDS = [
    "OBJECTID", "GLOBALID",
    "SHAPE", "SHAPE_AREA", "SHAPE_LENGTH"
]

if __name__ == "__main__":

    # TODO: Update me
    READY_TO_ADD_TO_REPLICA = False

    # TODO: Update me
    REPLICA_NAME = 'ADM_Rosde'  # Do not need to include SDEADM

    SUBTYPES = False
    TOPOLOGY_DATASET = False

    SUBTYPE_FIELD = ""
    SUBTYPE_DOMAINS = {}

    add_editor_tracking = True
    if add_editor_tracking:
        SDSF_IGNORE_FIELDS.extend(["ADDBY", "ADDDATE", "MODBY", "MODDATE"])

    # TODO: Update me
    sdsf = r"T:\work\giss\monthly\202402feb\gallaga\ADM_traffic_analyst_zone\SDSform_ADM_Transportation_Analysis_Zone.xlsx"

    sheet_name = "DATASET DETAILS"

    # TODO: Update me
    unique_id_fields = {
        'ADM_transportation_analysis_zone': [
            {
                "field": "TAZ_ID",
                "prefix": ""
            },
        ]
    }

    # TODO: Update me
    new_domain_types = {
        # "AST_EV_op_hour": "SHORT",
        # "AST_EV_output": "LONG"
    }

    CURRENT_DIR = os.getcwd()

    for dbs in [
        [utils.create_fgdb(out_folder_path=CURRENT_DIR, out_name="scratch.gdb")],
        # [
        #     config.get("SERVER", "dev_rw"),
        #     config.get("SERVER", "dev_ro"),
        # ],
        # [
        #     config.get("SERVER", "qa_rw"),  # qa_ro, qa_web_ro will get copied to db when processing rw
        #     config.get("SERVER", "qa_web_ro_gdb"),
        # ],
        # [
        #     config.get("SERVER", "prod_rw"),  # qa_ro, qa_web_ro will get copied to db when processing rw
        #     config.get("SERVER", "prod_ro"),
        # ],

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

                if feature_shape.upper() == "LINE":
                    feature_shape = "Polyline"

                field_data = fields_report.field_details

                domains_report = DomainsReport(xl_file)

                domain_data, domain_dataframes = domains_report.domain_info()
                domain_names = list(domain_data.keys())

                if SUBTYPES:
                    subtype_info = fields_report.subtype_info()
                    subtype_field = subtype_info.get("subtype_field")
                    subtype_field = \
                    [value.get("subtype_field") for key, value in domain_data.items() if value.get("subtype_field")][0]
                    subtype_domains_field = subtype_info.get("subtype_domains_field")
                    subtype_data = {key: value for key, value in domain_data.items() if
                                    domain_data[key].get("subtype_code")}

                if db_type == "GDB":

                    # Transfer existing domains to local dgb and find new domains not in SDE
                    new_domains = transfer_domains(
                        domains=domain_names,
                        output_workspace=db,
                        from_workspace=SDE
                    ).get("unfound_domains")

                else:
                    # Check for new domains not found in sde
                    domains_in_sde, new_domains = domains_in_db(db, domain_names)

                # Create any new domains
                if new_domains:
                    print(f"\nNew domains to create: {', '.join(new_domains)}")
                    # These should all be found in fields_report.field_details

                    for domain in new_domains:

                        try:
                            field_type = "TEXT"

                            if domain in new_domain_types:
                                field_type = new_domain_types.get(domain)

                            # Check if domain is a subtype domain
                            if SUBTYPE_DOMAINS:
                                if domain in [d["domain"] for d in SUBTYPE_DOMAINS["domains"]]:
                                    field_type = "LONG"
                                    print("\t*Subtype Domain Found!")

                            print(f"\n\tCreating domain '{domain}'...")
                            arcpy.CreateDomain_management(
                                in_workspace=db,
                                domain_name=domain,
                                field_type=field_type,
                                domain_type="CODED",
                                domain_description="",
                                split_policy="DUPLICATE"
                            )
                            # Sometimes this says it 'fails', but domain still gets created

                        except arcpy.ExecuteError:
                            arcpy_msg = arcpy.GetMessages(2)
                            print(f"Arcpy Error: {arcpy_msg}")
                            print(f"^^^*(Sometimes this fails in the script, but domain still gets created.)")

                        domain_df = domain_dataframes.get(domain)

                        # Populate new domains with codes and values:
                        sort_key = lambda x: x.Description

                        if SUBTYPE_DOMAINS:
                            if domain in [d["domain"] for d in SUBTYPE_DOMAINS["domains"]]:
                                sort_key = lambda x: x.Code

                        for row in sorted([x for x in domain_df.itertuples()], key=sort_key):
                            code = row.Code
                            desc = row.Description

                            print(f"\tAdding ({code}: {desc})")
                            arcpy.AddCodedValueToDomain_management(
                                in_workspace=db,
                                domain_name=domain,
                                code=code,
                                code_description=desc
                            )

                else:
                    print("\nNO new domains to create.")

                # Create the feature and add fields
                if (db_type == "SDE" and db_rights == "RW") or (db_type == "GDB" and not db_rights):

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

                        if field_name not in SDSF_IGNORE_FIELDS:
                            alias = row["Alias"]
                            field_type = row["Field Type"]
                            field_len = field_length
                            nullable = row["Nullable"]
                            default_value = row["Default Value"]
                            domain = row["Domain"] or "#"

                            if field_length:
                                field_length = int(field_length)

                            if field_type == "TEXT" and not field_length:
                                raise ValueError(
                                    f"Field {field_name} of type {field_type} needs to have a field length.")

                            new_feature.add_field(
                                field_name=field_name.upper(),
                                field_type=field_type,
                                length=field_len,
                                alias=alias,
                                # nullable=nullable,
                                domain_name=domain
                            )

                            if domain and domain != "#":
                                print(f"\t\t{field_name} has domain: '{domain}'")
                                new_feature.assign_domain(
                                    field_name=field_name,
                                    domain_name=domain,
                                    subtypes="#"
                                )

                            # Apply default values for fields, if applicable
                            if default_value:
                                new_feature.add_field_default(
                                    field=field_name,
                                    default_value=default_value
                                )

                    # ADD GLOBAL IDS
                    new_feature.add_gloablids()

                    if add_editor_tracking:
                        # ADD EDITOR TRACKING FIELDS
                        if db_type in ("SDE", "GDB") and db_rights in ("RW", ""):
                            new_feature.add_editor_tracking_fields()

                    # Update Privileges
                    if db_type != "GDB":
                        new_feature.change_privileges(
                            user="PUBLIC",
                            view="GRANT"
                        )

                        for user in EDIT_PERMISSIONS_USERS:
                            print(f"\nEnabling privileges for {user}")
                            arcpy.ChangePrivileges_management(
                                in_dataset=new_feature.feature,
                                user=user,
                                Edit="GRANT"
                            )

                    # SUBTYPES
                    if SUBTYPES:
                        create_subtype(new_feature.feature, SUBTYPE_FIELD, SUBTYPES, SUBTYPE_DOMAINS)

                    if db_type == "SDE" and db_rights == "RW":

                        # Register as Versioned
                        new_feature.register_as_versioned()  # needs to be versioned to add to replica

                        # COPY FEATURE TO RO, WEBGIS
                        ro_sdeadm_db = db.replace("RW", "RO")
                        ro_webgis_db = ro_sdeadm_db.upper().replace("SDEADM", "WEBGIS")

                        ro_sdeadm_feature = os.path.join(ro_sdeadm_db, new_feature.feature_name)
                        ro_webgis_feature = os.path.join(ro_webgis_db, new_feature.feature_name)

                        for ro_feature, ro_db in (ro_sdeadm_feature, ro_sdeadm_db), (ro_webgis_feature, ro_webgis_db):

                            # Don't need to add to WEB if feature is a table
                            if ro_db == ro_webgis_db and feature_shape.upper() == 'ENTERPRISE GEODATABASE TABLE':
                                print(f"\nFeature is a table - skipping adding to WEB RO...")
                                continue

                            if not arcpy.Exists(ro_feature):
                                print(f"\tCopying RW feature to {ro_db}...")

                                # Need to use table to table if a table...
                                if feature_shape.upper() == 'ENTERPRISE GEODATABASE TABLE':
                                    feature = arcpy.TableToTable_conversion(
                                        in_rows=new_feature.feature,
                                        out_path=ro_db,
                                        out_name=new_feature.feature_name
                                    )[0]

                                else:
                                    feature = arcpy.FeatureClassToFeatureClass_conversion(
                                        in_features=new_feature.feature,
                                        out_path=ro_db,
                                        out_name=new_feature.feature_name,
                                    )[0]

                        if READY_TO_ADD_TO_REPLICA:
                            replicas.add_to_replica(
                                replica_name=REPLICA_NAME,
                                rw_sde=db,
                                ro_sde=ro_sdeadm_db,
                                add_features=[new_feature.feature],
                                topology_dataset=TOPOLOGY_DATASET
                            )

                        # Un-version RO feature, disable editor tracking, index
                        for feature in ro_sdeadm_feature, ro_webgis_feature:

                            if arcpy.Exists(
                                    feature):  # ro_webgis_feature may not have ever gotten created if it was a table.

                                print(f"\tRegistering as UN-versioned for '{feature}'...")
                                arcpy.UnregisterAsVersioned_management(in_dataset=feature)

                                if add_editor_tracking:
                                    print(f"\tDisabling Editor Tracking for '{feature}'...")
                                    arcpy.DisableEditorTracking_management(in_dataset=feature)

                                # Set privileges
                                ro_users = ["PUBLIC", "SDE"]

                                for user in ro_users:
                                    arcpy.ChangePrivileges_management(
                                        in_dataset=feature,
                                        user="PUBLIC",
                                        View="GRANT"
                                    )
                                    arcpy.ChangePrivileges_management(
                                        in_dataset=feature,
                                        user=user,
                                        View="GRANT"
                                    )

                                if feature_name in unique_id_fields:
                                    id_field_info = unique_id_fields[feature_name]

                                    for field_info in id_field_info:
                                        id_field = field_info.get("field")

                                        print(f"\nAdding attribute index on {id_field}...")
                                        try:
                                            arcpy.AddIndex_management(
                                                in_table=feature,
                                                fields=id_field,
                                                index_name=f"index_{id_field}",
                                                ascending="ASCENDING"
                                            )

                                        except arcpy.ExecuteError:
                                            arcpy_msg = arcpy.GetMessages(2)
                                            print(arcpy_msg)

                    if add_editor_tracking:
                        # ENABLE EDITOR TRACKING
                        new_feature.enable_editor_tracking()

                    # Attribute Rules - Add after feature has been copied to Read-Only. RW and .gdb only
                    if feature_name in unique_id_fields:
                        id_field_info = unique_id_fields[feature_name]

                        for field_info in id_field_info:
                            id_field = field_info.get("field")
                            prefix = field_info.get("prefix")

                            print(f"Creating Sequence and Attribute Rule for {id_field} with prefix {prefix}...")

                            attribute_rules.add_sequence_rule(
                                workspace=db,
                                feature_name=new_feature.feature,
                                field_name=id_field,
                                sequence_prefix=prefix,
                            )

                            print(f"\nAdding attribute index on {id_field}...")
                            try:
                                arcpy.AddIndex_management(
                                    in_table=new_feature.feature,
                                    fields=id_field,
                                    index_name=f"index_{id_field}",
                                    ascending="ASCENDING"
                                )

                            except arcpy.ExecuteError:
                                arcpy_msg = arcpy.GetMessages(2)
                                print(arcpy_msg)

    # Checks:
    # Replicas
    # Indexes
    # Attribute Rules
    # Default values
    # Domains
    # Privileges assigned
    # Versioned
    # Editor Tracking
    # Features in RO, WEB_RO

    # Add to CMDB
