import os
import arcpy

import pandas as pd

import utils
import submission_form

arcpy.env.overwriteOutput = True

FEATURE_TEMPLATE_XL = r"T:\work\giss\monthly\202209sept\gallaga\Pedestrian Ramps\Pedestrian Ramps Tactiles 10May2022.xlsx"
FIELDS_SHEET = "AST_ped_ramp"
FEATURE_TYPE = "POINT"  # POINT, POLYGON, POLYLINE

SDE_PROD_RW = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\PROD_RW_SDEADM.sde"

submission_form = submission_form.SubmissionForm(FEATURE_TEMPLATE_XL, FIELDS_SHEET)

# Create local workspace
gdb = utils.create_fgdb(out_folder_path=os.getcwd())

# Create feature
print(f"\nCreating new feature {submission_form.sheet_name}...")
new_feature = arcpy.arcpy.CreateFeatureclass_management(
    out_path=gdb,
    out_name=submission_form.sheet_name,
    geometry_type=FEATURE_TYPE
)

sde_domains = {x.name: x.codedValues for x in arcpy.da.ListDomains(SDE_PROD_RW)}

# Get domains from Submission form
sf_domains = submission_form.domains
sf_sheets = submission_form.sheets

new_domains = [sheet.replace("Domain ", "") for sheet in sf_sheets if "DOMAIN" in sheet.upper()]

sde_transfer_domains = [x for x in sf_domains if x in sde_domains]
unfound_sf_domains = [x for x in sf_domains if x not in sde_domains and x not in new_domains]  # Check if these are NEW domains

if unfound_sf_domains:
    raise ValueError(f"A domain is referenced that is NOT found in SDE or as a new domain in the SDSF.\n\t{', '.join(unfound_sf_domains)}")

# Transfer domains from SDE to workspace
# for domain in sde_transfer_domains:
#
#     table = os.path.join(gdb, f"{domain}_domain")
#     print(f"\nDomain ('{domain}') to table: '{table}'...")
#
#     domain_tbl = arcpy.DomainToTable_management(
#         in_workspace=SDE_PROD_RW,
#         domain_name=domain,
#         out_table=table,
#         code_field="CODE",
#         description_field="VALUE"
#     ).getOutput(0)
#
#     # Add domains from table to workspace
#     print("\tCreating domain from table...")
#     arcpy.TableToDomain_management(
#         in_table=domain_tbl,
#         code_field="CODE",
#         description_field="VALUE",
#         in_workspace=gdb,
#         domain_name=domain,
#         domain_description=domain
#     )

# Create new Domains
domain_dfs = submission_form.new_domains()
print("\nSetting up new domains...")
for domain in domain_dfs:
    print(domain)
    domain_info = domain_dfs[domain]

    # TODO: Seem to have to manually create domains
    # arcpy.CreateDomain_management(
    #     in_workspace=gdb,
    #     domain_name=domain,
    #     domain_description=domain,
    #     field_type="TEXT",
    #     domain_type="CODED"
    # )

    for index, row in domain_info.iterrows():
        code = row[0]
        value = row[1]

        try:
            print(f"\tAdding ({code}: {value}) to '{domain}' domain")
            arcpy.AddCodedValueToDomain_management(
                in_workspace=gdb,
                domain_name=domain,
                code=code,
                code_description=value
            )
        except arcpy.ExecuteError as e:
            print(e)
            print(arcpy.GetMessages(2))


# feature_schema_info = submission_form.df
# for index, row in feature_schema_info.iterrows():
#     field_name = row[0]
#     field_index = row[1]
#     field_type = row[2]
#     field_length = row[3] if not pd.isna(row[3]) else None
#     field_alias = row[4]
#     field_desc = row[5]
#     field_domain = row[6] if not pd.isna(row[6]) else None  # TODO: No domains being applied
#     field_default = row[7] if not pd.isna(row[7]) else None
#     field_isnullable = row[8]
#     field_precision = row[9] if not pd.isna(row[9]) else None
#     field_scale = row[10] if not pd.isna(row[10]) else None
#
#     print(f"{index}/{len(feature_schema_info.iterrows())}) {field_name}")
#
#     # Apply field mapping
#     print(f"\tAdding field '{field_name}'...")
#     arcpy.AddField_management(
#         in_table=new_feature,
#         field_name=field_name,
#         field_type=field_type,  # TEXT, FLOAT, DOUBLE, SHORT, LONG, DATE, BLOB, RASTER, GUID
#         field_precision=field_precision,
#         field_scale=field_scale,  # For FLOAT, DOUBLE field types
#         field_length=field_length,  # For TEXT field types
#         field_alias=field_alias,
#         field_is_nullable=field_isnullable,  # NULLABLE, NON_NULLABLE
#         # field_is_required="#",  # NON_REQUIRED, REQUIRED
#         field_domain=field_domain
#     )


    # Set field default

# Set index fields
# arcpy.AddIndex_management(
#     in_table,
#     fields,
#     {index_name},
# )
# Check for subtypes
# Create new domains
