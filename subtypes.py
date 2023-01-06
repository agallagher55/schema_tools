import arcpy
import os


def create_subtype(feature: str, subtype_field: str, subtypes: dict):
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
        in_table=subtype_feature,
        field=subtype_field
    )

    for code in subtypes:
        subtype_desc = subtypes[code]
        print(f"\tAdding subtype {code}: {subtype_desc}...")
        arcpy.AddSubtype_management(
            in_table=subtype_feature,
            subtype_code=code,
            subtype_description=subtype_desc
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
    create_subtype(subtype_feature, SUBTYPE_FIELD, SUBTYPES)
