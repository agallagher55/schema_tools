import os
import arcpy

import connections
import attribute_rules
import utils
import replicas

from configparser import ConfigParser

from domains import transfer_domains, domains_in_db
from subtypes import create_subtype

from SpatialDataSubmissionForms.features import Feature
from SpatialDataSubmissionForms.reporter import FieldsReport, DomainsReport

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

MAX_TABLE_NAME_LENGTH = 27

config = ConfigParser()
config.read('config.ini')

SUBTYPES = True
TOPOLOGY_DATASET = False

READY_TO_ADD_TO_REPLICA = True
REPLICA_NAME = "LND_Rosde"

# SDE = config.get("LOCAL", "prod_rw")
SDE = config.get("SERVER", "prod_rw")

SPATIAL_REFERENCE = os.path.join(SDE, "SDEADM.LND_hrm_parcel_parks", "SDEADM.LND_hrm_park")

USER_PRIVILEGE = "PUBLIC"
VIEW_PRIVILEGE = "GRANT"

IMMUTABLE_FIELDS = {
    "OBJECTID", "GLOBALID", "ADDBY", "ADDDATE",
    "MODBY", "MODDATE", "SHAPE", "SHAPE_AREA", "SHAPE_LENGTH"
}


if __name__ == "__main__":
    sdsf = r"T:\work\giss\monthly\202301jan\gallaga\Artisan Vendors\Food_Artisan_Vendors_Feature_Class.xlsx"
    sheet_name = "DATASET DETAILS"

    unique_id_fields = {
        'LND_food_artisan_vendors': [
            {
                "field": "VEND_ID",
                "prefix": "VEN"
            },
        ]

    }

    SUBTYPE_FIELD = "VENDRTYP"
    SUBTYPES = {
        "1": "Food Service Vehicle",
        "2": "Food Stand",
        "3": "Artisan Stand"
    }

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
        # [config.get("SERVER", "dev_rw")],
        [config.get("SERVER", "qa_rw")],
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

                feature_name = fields_report.feature_class_name[:MAX_TABLE_NAME_LENGTH]  # Should be all lower case except for the prefix
                feature_shape = fields_report.feature_shape

                if feature_shape == "Line":
                    feature_shape = "Polyline"

                field_data = fields_report.field_details

                if SUBTYPES:
                    subtype_info = fields_report.subtype_info()
                    subtype_field = subtype_info.get("subtype_field")
                    subtype_domains_field = subtype_info.get("subtype_domains_field")

                domains_report = DomainsReport(xl_file, subtype_field)

                domain_data, domain_dataframes = domains_report.domain_info()
                domain_names = list(domain_data.keys())
                subtype_data = {key: value for key, value in domain_data.items() if domain_data[key].get("subtype_code")}
                subtype_field = [value.get("subtype_field") for key, value in domain_data.items() if value.get("subtype_field")][0]

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
                            arcpy.management.AddCodedValueToDomain(
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
                        feature_name=feature_name + "_test",
                        geometry_type=feature_shape,
                        spatial_reference=SPATIAL_REFERENCE
                    )

                    print("\nAdding Fields...")
                    feature_fields = field_data["Field Name"].values

                    for row_num, row in field_data.iterrows():

                        alias = row["Alias"]
                        field_type = row["Field Type"]
                        field_len = field_length
                        nullable = row["Nullable"]
                        default_value = row["Default Value"]
                        domain = row["Domain"] or "#"

                        if field_length:
                            field_length = int(field_length)

                        if not field_length and field_type == "TEXT":
                            raise ValueError(f"Field {field_name} of type {field_type} needs to have a field length.")

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
                                domain_name=domain,
                                subtypes="#"
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

                    # SUBTYPES
                    create_subtype(new_feature.feature, SUBTYPE_FIELD, SUBTYPES, SUBTYPE_DOMAINS)

                    if db_type == "SDE" and db_rights == "RW":

                        if READY_TO_ADD_TO_REPLICA:

                            # Register as Versioned
                            new_feature.register_as_versioned()

                            # Copy RW feature to RO
                            ro_sde_db = db.replace("RW", "RO")
                            ro_exists = arcpy.Exists(ro_sde_db)

                            # TODO: Do we need to copy to web_ro.gdb ? Or only if, and when, we need to publish service?
                            ro_feature = os.path.join(ro_sde_db, new_feature.feature_name)

                            if not arcpy.Exists(ro_feature):
                                print("\tCopying RW feature to RO db...")

                                # TODO: Will need to use table to table if a table...
                                ro_feature = arcpy.conversion.FeatureClassToFeatureClass(
                                    in_features=new_feature.feature,
                                    out_path=ro_sde_db,
                                    out_name=new_feature.feature_name,
                                )[0]

                            # Add feature to replica
                            replicas.add_to_replica(
                                replica_name=REPLICA_NAME,
                                rw_sde=db,
                                ro_sde=ro_sde_db,
                                add_features=[new_feature.feature],
                                topology_dataset=TOPOLOGY_DATASET
                            )

                            # Un-version RO feature.
                            print("\tRegistering RO feature as UN-versioned...")
                            arcpy.UnregisterAsVersioned_management(in_dataset=ro_feature)

                    # Update Privileges
                    new_feature.change_privileges(
                        user=USER_PRIVILEGE,
                        view=VIEW_PRIVILEGE
                    )

                    # ENABLE EDITOR TRACKING
                    new_feature.enable_editor_tracking()

                    # Attribute Rules - Add after feature has been copied to Read-Only. RW and .gdb only
                    if feature_name in unique_id_fields:

                        for field_info in unique_id_fields.get(feature_name):
                            id_field = field_info.get("field")
                            prefix = field_info.get("prefix")

                            print(f"Creating Sequence and Attribute Rule for {id_field} with prefix {prefix}...")

                            attribute_rules.add_sequence_rule(
                                workspace=db,
                                feature_name=new_feature.feature,
                                field_name=id_field,
                                sequence_prefix=prefix
                            )

                            print(f"\nAdding attribute index on {id_field}...")
                            try:
                                arcpy.AddIndex_management(
                                    in_table=new_feature.feature,
                                    fields=id_field,
                                    index_name=f"unique_index{id_field}",
                                    unique="NON_UNIQUE",
                                    ascending="ASCENDING"
                                )

                            except arcpy.ExecuteError:
                                arcpy_msg = arcpy.GetMessages(2)
                                print(arcpy_msg)


# TODO: Add to WGS84 script once in prod. (DC1-GIS-APP-P22)
