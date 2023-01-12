import arcpy
import os


def create_subtype(feature: str, subtype_field: str, subtypes: dict, subtype_domains):
    """
    Creates subtypes for a feature class based on a specified subtype field and a dictionary of subtype codes and
        descriptions.

    param: feature (str): The path to the feature class.
    param: subtype_field (str): The field in the feature class that will be used for subtyping.
    param: subtypes (dict): A dictionary where the keys are subtype codes and the values are subtype descriptions.
    """

    print(f"\nCreating subtypes...")

    print(f"Setting subtype field on {feature} to {subtype_field}...")
    arcpy.SetSubtypeField_management(
        in_table=feature,
        field=subtype_field
    )

    for code in subtypes:
        subtype_desc = subtypes[code]
        print(f"\tAdding subtype {code}: {subtype_desc}...")
        arcpy.AddSubtype_management(
            in_table=feature,
            subtype_code=code,
            subtype_description=subtype_desc
        )

    if subtype_domains:
        domain_field = subtype_domains.get("field")
        domains_info = subtype_domains.get("domains")

        for info in domains_info:
            subtype_code = info["code"]
            domain = info["domain"]

            arcpy.AssignDomainToField_management(
                in_table=feature,
                field_name=domain_field,
                domain_name=domain,
                subtype_code=subtype_code
            )


if __name__ == "__main__":
    workspace = os.path.join(os.getcwd(), "scratch.gdb")
    subtype_feature = os.path.join(workspace, "LND_food_artisan_vendors")

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

    create_subtype(subtype_feature, SUBTYPE_FIELD, SUBTYPES, SUBTYPE_DOMAINS)
