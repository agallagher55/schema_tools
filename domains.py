import arcpy

from typing import Sequence


def add_code_value(workspace, domain_name, code, value):
    # TODO: Check if code already exists

    print(f"\nAdding domain code, value: '{code}' & '{value}' to domain '{domain_name}'...")

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


def transfer_domains(domains: Sequence[str], output_workspace, from_workspace):
    """

    :param domains:
    :param output_workspace:
    :param from_workspace:
    :return:
    """

    print(f"\nTransferring domains from {from_workspace} to {output_workspace}...")

    from_workspace_domains = {x.name: x.codedValues for x in arcpy.da.ListDomains(from_workspace)}
    output_workspace_domains = [x.name for x in arcpy.da.ListDomains(output_workspace)]
    
    unfound_domains = list()

    for count, domain in enumerate(domains, start=1):
        print(f"\n{count}/{len(domains)}) Domain: '{domain}'")

        domain_info = from_workspace_domains[domain]

        # Check that domain is in output_workspace_domains
        if domain not in from_workspace_domains:
            unfound_domains.append(domain)
            print(f"Did not find '{domain}' in source workspace - {output_workspace}")

        if domain not in output_workspace_domains:
            arcpy.CreateDomain_management(
                in_workspace=output_workspace,
                domain_name=domain,
                domain_description=domain,
                field_type="TEXT",
                domain_type="CODED"
            )

            for code, value in domain_info.items():
                print(f"\tAdding ({code}: {value})")
                arcpy.AddCodedValueToDomain_management(
                    in_workspace=output_workspace,
                    domain_name=domain,
                    code=code,
                    code_description=value
                )

        else:
            print(f"\t'{domain}' is already in the output workspace!")

    return {"unfound_domains": unfound_domains, "domains": domains}
