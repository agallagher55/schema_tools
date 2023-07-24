import os.path

import arcpy


def check_for_rules(feature, rules: list):
    """

    :param feature:
    :param rules:
    :return:
    """

    print(f"\nChecking for Attribute Rules in {feature}...")

    rules = [x.upper().strip() for x in rules]
    feature_rules = arcpy.Describe(feature).attributeRules

    rules_found = [r.name.upper().strip() for r in feature_rules]
    rules_not_found = [x.upper().strip() for x in rules if x not in rules_found]

    if rules_not_found:
        print(f"\t*Did NOT find rule(s): {' ,'.join(rules_not_found)}")
        print(f"\tRules found: {' ,'.join(rules_found)}")
        return False

    return True


def toggle_rule(rule_names: list, rule_type: str, feature, enable_disable: str):
    """
    - Turn rule ON or OFF using ENABLE, DISABLE keyword

    :param rule_names: list of rule names (GP tool takes list of rules)
    :param rule_type: CALCULATION, CONSTRAINT, VALIDATION
    :param feature: path to feature
    :param enable_disable: ENABLE, DISABLE
    :return:
    """

    if enable_disable.upper() not in ("ENABLE", "DISABLE"):
        raise ValueError(f"Missing parameter of enable or disable")

    rules_not_found = check_for_rules(feature, rule_names)

    if rules_not_found:
        raise IndexError(f"Unable to find {rules_not_found} in feature {feature}")

    if enable_disable.upper() == "ENABLE":
        print(f"\tEnabling Attribute Rules ({', '.join(rule_names)})...")
        arcpy.EnableAttributeRules_management(
            in_table=feature,
            names=rule_names,
            type=rule_type
        )

    elif enable_disable.upper() == "DISABLE":
        print(f"\tEnabling Attribute Rules ({', '.join(rule_names)})...")
        arcpy.DisableAttributeRules_management(
            in_table=feature,
            names=rule_names,
            type=rule_type
        )


def add_sequence_rule(workspace, feature_name, field_name, sequence_prefix=""):
    print("\nAdding Sequence Attribute Rule...")

    rule_description = f"{os.path.basename(feature_name)} - {field_name} - Generate ID"
    expression = f"'{sequence_prefix}' + NextSequenceValue('sdeadm.{field_name}')"  # for SDE features
    
    if field_name in ("ASSETID", "ASSET_ID"):
        raise ValueError(f"Sequence for {field_name} needs a different sequence name.")

    in_feature = os.path.join(workspace, feature_name)

    # Make sure Attribute Rule does not already exist.
    rule_exists = check_for_rules(
        feature=os.path.join(workspace, feature_name),
        rules=[rule_description]
    )

    if rule_exists:
        print(f"Rule '{rule_description}' already exists!")
        return True

    if ".gdb" in workspace:
        expression = f"'{sequence_prefix}' + NextSequenceValue('{field_name}')"

    try:
        arcpy.DeleteDatabaseSequence_management(
            in_workspace=workspace,
            seq_name=field_name
        )

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))

    finally:
        print(f"\tCreating db sequence {field_name}...")
        arcpy.CreateDatabaseSequence_management(
            in_workspace=workspace,
            seq_name=field_name,
            seq_start_id=1,
            seq_inc_value=1
        )

    print("\tAdding Attribute Rule...")
    print(f"\t\tExpression: {expression}")
    arcpy.AddAttributeRule_management(
        in_table=in_feature,
        name=rule_description,
        type="CALCULATION",
        script_expression=expression,
        is_editable="NONEDITABLE",
        triggering_events="INSERT",
        # error_number="optional",
        # error_message="optional",
        description=rule_description,
        # subtype="optional",
        field=field_name,
        exclude_from_client_evaluation="EXCLUDE",
        batch="NOT_BATCH",
        # severity="optional",
        tags="sequence;"
    )


if __name__ == "__main__":
    trn_bridge = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_RW_SDE.sde\SDEADM.TRN_bridge"
    RULE_NAMES = ['TRN_bridge - ASSETID - Generate ID', 'TRN_bridge - BRIDGEID - Generate ID']
    RULE_TYPE = "CALCULATION"

    rules_not_found = check_for_rules(trn_bridge, RULE_NAMES)

    # Turn off Services
    # Disable Editor Tracking

    # # Disable rule
    # toggle_rule(RULE_NAMES, RULE_TYPE, trn_bridge, "disable")

    # --------- DATA CHANGES --------- #

    # Enable rule
    # toggle_rule(RULE_NAMES, RULE_TYPE, trn_bridge, "enable")
    # Enable Editor Tracking
    # Turn On services
