import arcpy


def add_code_value(workspace, domain_name, code, value):
    # TODO: Check if code already exists

    print(f"\nAdding domain code, value: '{code}' & '{value}'...")

    arcpy.AddCodedValueToDomain_management(
        in_workspace=workspace,
        domain_name=domain_name,
        code=code,
        code_description=value
    )


def remove_code_value(workspace, domain_name, code):
    # TODO: Check if code exists first

    print(f"\nRemoving domain code: '{code}' from {domain_name}...")

    arcpy.DeleteCodedValueFromDomain_management(
        workspace,
        domain_name,
        code
    )


def domain_in_db(db, domain):
    """
    - Make sure domain exists in database
    :param db:
    :param domain:
    :return:
    """

    domains = [domain.name for domain in arcpy.da.ListDomains(db)]

    if domain not in domains:
        return False, domains

    return True, domains


def assign_to_field(feature, domain_name, field_name, subtypes: list):
    print(f"\nAssigning domain '{domain_name}' to field '{field_name}...'")

    arcpy.AssignDomainToField_management(
        in_table=feature,
        field_name=field_name,
        domain_name=domain_name,
        subtype_code=subtypes  # Optional
    )
