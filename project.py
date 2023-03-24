"""
List features by creation date
    SELECT OWNER, OBJECT_NAME, CREATED
      FROM dba_objects
      WHERE object_type = 'TABLE'
        AND OWNER IN ('WEBGIS')
        AND SECONDARY = 'N'
        AND OBJECT_NAME NOT LIKE 'KEYSET%'
      ORDER BY CREATED DESC

Get all WEBGIS features not in WGS84
Re-project WEBGIS features if needed
"""

import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)


features = [
    "ADM_parking_collection_zones",
    "LND_SPECIAL_PLANNING_AREAS",
    "LND_OFF_LEASH_AREA",
    "AST_PED_RAMP",
    "TRN_TRANSIT_SHELTER",
    "TRN_traffic_calming_assessm"
]


def reproject(input_fc: str, output_gdb: str, output_sr=None, transformations=None):
    """
    Reprojects a feature class from one coordinate system to another.

    Parameters:
    -----------
    input_fc : str - Path to the input feature class to be reprojected.
    output_gdb : str - Path to the geodatabase where the output feature class will be stored.
    output_sr : arcpy.SpatialReference, optional - The output spatial reference.
        If None, the default is "WGS 1984 Web Mercator (Auxiliary Sphere)".

    Returns:
    --------
    None.

    Example:
    --------
    reproject("C:/data/input.gdb/input_fc", "C:/data/output.gdb/output_fc", "C:/data/output.gdb")

    """

    desc = arcpy.Describe(input_fc)

    feature_name = desc.name
    input_sr = desc.spatialReference
    output_fc = os.path.join(output_gdb, feature_name)

    # Validate input parameters
    if not arcpy.Exists(input_fc):
        raise ValueError("Input feature class does not exist.")

    if not arcpy.Exists(output_gdb):
        raise ValueError("Output geodatabase does not exist.")

    if input_sr.name == "Unknown" or input_sr.name != 'NAD_1983_CSRS_2010_MTM_5_Nova_Scotia':
        print(f"Input Spatial Reference: {input_sr.name}")
        raise ValueError("Input feature class does not have a valid spatial reference.")

    if not output_sr:
        output_sr = arcpy.SpatialReference(3857)

    if arcpy.Exists(output_fc):
        arcpy.Delete_management(output_fc)

    if not transformations:
        transformations = "NAD83_CSRS_1997_to_NAD83_CSRS_2010; NAD_1983_CSRS_To_WGS_1984_2;"

    print(f"\tUsing transformations: '{transformations}'")
    print(f"\tInput spatial reference: '{input_sr.name}'")
    print(f"\tOutput spatial reference: '{output_sr.name}'")

    try:
        with arcpy.EnvManager(outputCoordinateSystem=output_sr, geographicTransformations=transformations):
            arcpy.Project_management(
                input_fc,
                output_fc,
                output_sr
            )

        print(f"\n\tFeature class re-projected to {output_fc}.")
        return output_fc

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))



if __name__ == "__main__":

    LOCAL_GDB = r"T:\work\giss\monthly\202303mar\gallaga\Parking Collection Zones\scripts\scratch.gdb"

    SDE = r"E:\HRM\Scripts\SDE\prod_RO_webgis.sde"
    # sde = R"E:\HRM\Scripts\SDE\qa_RO_webgis.sde"

    with arcpy.EnvManager(workspace=SDE):
        for feature in features:

            desc = arcpy.Describe(feature)
            sr = desc.spatialReference

            if sr.name == "NAD_1983_CSRS_2010_MTM_5_Nova_Scotia":
                print(f"\nFeature: {feature}")

                # project to local workspace
                reprojected_feature = reproject(feature, LOCAL_GDB)

                # from_fc, to_fc, to_fc_name
                # reproject(
                # 'E:\\\\HRM\\\\Scripts\\\\SDE\\\\qa_RO_sdeadm.sde\\SDEADM.TRN_streets_routes\\SDEADM.TRN_street',
                # 'E:\\HRM\\Scripts\\Python3\\Project_to_WGS84\\\\Scratch\\Scratch.gdb\\TRN_street',
                # '\\\\msfs201\\GISApp\\AGS_QA\\fgdbs\\web_RO.gdb\\TRN_street'
                # )

