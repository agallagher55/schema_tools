import arcpy
import os


def transfer_features(features: list, output_workspace: str) -> list:

    """
    The transfer_features function takes a list of features and an output workspace as arguments.
    It then copies each feature to the output workspace, returning a list of the copied features.

    :param features: list: Pass in the list of features that are to be transferred
    :param output_workspace: str: Specify the workspace where the features will be copied to
    :return: A list of the copied features
    """

    out_features = list()

    print(f"\nTransferring features to {output_workspace}...")

    for feature in features:
            desc = arcpy.Describe(feature)

            feature_name = desc.name.replace("SDEADM.", "")
            out_feature = os.path.join(output_workspace, feature_name)

            arcpy.Copy_management(
                in_data=feature,
                out_data=out_feature
            )
            print(arcpy.GetMessages())

            out_features.append(out_feature)

    return out_features


def remove_domain(feature: str, fields: list) -> str:

    """
    The remove_domain function removes the domain assigned to fields in the 'feature' feature.

    :param feature: str: Specify the feature class that will have its domain removed
    :param fields: list: Pass a list of fields to the remove_domain function
    :return: The feature class
    """

    print(f"\nRemoving domain assigned to fields in the '{feature}' feature...")

    for field in fields:
        arcpy.RemoveDomainFromField_management(
            in_table=feature,
            field_name=field
        )

    return feature
