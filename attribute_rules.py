import arcpy


def check_for_rules(feature, rules: list):
    """

    :param feature:
    :param rules:
    :return:
    """

    print(f"\nChecking for Attribute Rules in {feature}...")

    feature_rules = arcpy.Describe(feature).attributeRules

    rule_names = [r.name for r in feature_rules]
    rules_not_found = [x for x in rules if x not in rule_names]

    if rules_not_found:
        print(f"\t*Did NOT find rules: {' ,'.join(rules_not_found)}")

    return rules_not_found


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
