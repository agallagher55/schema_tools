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

    print(f"\nRemoving domain code: '{code}' from {domain_name}...")
    coded_values = [d.codedValues for d in arcpy.da.ListDomains(workspace) if d.name == domain_name]

    if coded_values:
        codes = list(coded_values[0].keys())
        if code not in codes:
            print("\tCode not found in domain!")
            return False

    arcpy.DeleteCodedValueFromDomain_management(
        workspace,
        domain_name,
        code
    )
    return True


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


def assign_to_field(feature, domain_name, field_name):
    print(f"\nAssigning domain '{domain_name}' to field '{field_name}...'")

    arcpy.AssignDomainToField_management(
        in_table=feature,
        field_name=field_name,
        domain_name=domain_name,
        subtype_code=None  # Optional
    )
