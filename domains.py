import arcpy
import functools

from typing import Sequence


def arcpy_messages(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            messages = arcpy.GetMessages()
            message_lines = messages.split("\n")

            for message in message_lines:
                if message:
                    print(f"\t{message}")

            return result

        except arcpy.ExecuteError as e:
            print(f"ARCPY ERROR: {e}")

    return wrapper


@arcpy_messages
def add_code_value(workspace, domain_name, code, value):
    """
    - Add domain code, value to domain domain_name
    :param workspace: 
    :param domain_name: 
    :param code: 
    :param value: 
    :return: 
    """
    
    # TODO: Check if code already exists

    print(f"\nAdding domain code, value: '{code}' & '{value}' to domain '{domain_name}'...")

    arcpy.AddCodedValueToDomain_management(
        in_workspace=workspace,
        domain_name=domain_name,
        code=code,
        code_description=value
    )


@arcpy_messages
def remove_code_value(workspace, domain_name, code):
    # TODO: Check if code exists first

    print(f"\nRemoving domain code: '{code}' from {domain_name}...")

    arcpy.DeleteCodedValueFromDomain_management(
        workspace,
        domain_name,
        code
    )


@arcpy_messages
def domains_in_db(db, domains):
    """
    - Make sure domain exists in database
    :param db:
    :param domains:
    :return:
    """

    print(f"\nChecking to see if domains {', '.join(domains)} exist in {db}...")

    db_domains = [domain.name for domain in arcpy.da.ListDomains(db)]
    unfound_domains = [d for d in domains if d not in db_domains]

    if unfound_domains:
        return False, unfound_domains

    return True, unfound_domains


@arcpy_messages
def assign_to_field(feature, domain_name, field_name, subtypes):
    print(f"\nAssigning domain '{domain_name}' to field '{field_name}...'")
    try:
        arcpy.AssignDomainToField_management(
            in_table=feature,
            field_name=field_name,
            domain_name=domain_name,
            subtype_code=subtypes  # Optional
        )
    except arcpy.ExecuteError as e:
        print(e)


@arcpy_messages
def transfer_domains(domains: Sequence[str], output_workspace, from_workspace) -> dict:
    """
    - Transfer domains from from_workspace to output_workspace. Only domain types of CODED, TEXT will be valid

    :param domains: domains to transfer
    :param output_workspace: where domains will be trasferred to
    :param from_workspace: will domains will be transferred from
    :return: {"unfound_domains": unfound_domains, "domains": domains}
    """

    print(f"\nTransferring domains from {from_workspace} to {output_workspace}...")
    from_workspace_domains = {x.name: x.codedValues for x in arcpy.da.ListDomains(from_workspace)}
    output_workspace_domains = [x.name for x in arcpy.da.ListDomains(output_workspace)]

    unfound_domains = list()

    for count, domain in enumerate(domains, start=1):
        print(f"\n{count}/{len(domains)}) Domain: '{domain}'")

        # Check that domain doesn't already exist in output workspace
        if domain not in output_workspace_domains:

            arcpy.CreateDomain_management(
                in_workspace=output_workspace,
                domain_name=domain,
                domain_description=domain,
                field_type="TEXT",
                domain_type="CODED"
            )

            # Check that domain is in source workspace
            if domain not in from_workspace_domains:
                unfound_domains.append(domain)
                print(f"\tDid NOT find '{domain}' in source workspace - {from_workspace}")

                # Will need to get code, values from spreadsheet

            else:
                domain_info = from_workspace_domains.get(domain)

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
