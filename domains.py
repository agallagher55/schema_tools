import arcpy
import functools


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
def add_code_value(workspace: str, domain_name: str, code: str, value: str):
    """
    Adds a new code-value pair to an existing domain.
    :param workspace: A string specifying the path to the geodatabase containing the domain.
    :param domain_name: The name of the domain to add the code-value pair to.
    :param code: A string specifying the code to add to the domain.
    :param value: A string specifying the value associated with the code.
    :return: None
    """

    print(f"\nAdding domain code, value: '{code}' & '{value}' to domain '{domain_name}'...")

    arcpy.AddCodedValueToDomain_management(
        in_workspace=workspace,
        domain_name=domain_name,
        code=code,
        code_description=value
    )
    print(f"\tSuccessfully added code {code} with value {value} to domain {domain_name}.")


@arcpy_messages
def remove_code_value(workspace, domain_name, code):
    # TODO: Check if code exists first

    print(f"\nRemoving domain code: '{code}' from {domain_name}...")

    arcpy.DeleteCodedValueFromDomain_management(
        workspace,
        domain_name,
        code
    )
    print(f"\tSuccessfully removed code {code} from domain {domain_name}.")


@arcpy_messages
def domains_in_db(db, domains: list):
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
def transfer_domains(domains: list, output_workspace, from_workspace) -> dict:
    """
    - Transfer domains from from_workspace to output_workspace. Only domain types of CODED, TEXT will be valid

    :param domains: domains to transfer
    :param output_workspace: where domains will be trasferred to
    :param from_workspace: will domains will be transferred from
    :return: {"unfound_domains": unfound_domains, "domains": domains}
    """

    print(f"\nTransferring domains from '{from_workspace}' to '{output_workspace}'...")
    from_workspace_domains = {x.name: {"coded_values": x.codedValues, "type": x.type} for x in arcpy.da.ListDomains(from_workspace)}
    output_workspace_domains = [x.name for x in arcpy.da.ListDomains(output_workspace)]

    unfound_domains = list()

    for count, domain in enumerate(domains, start=1):
        print(f"{count}/{len(domains)}) Domain: '{domain}'")

        # Check for domain in source workspace
        if domain not in list(from_workspace_domains.keys()):
            unfound_domains.append(domain)
            print(f"\tDid NOT find '{domain}' in source workspace: {from_workspace}.\n\tThis will be created.")

        else:

            # Check for domain in output workspace
            if domain.upper() not in [d.upper() for d in output_workspace_domains]:

                field_type = from_workspace_domains.get(domain).get("type")

                # Create domain in output workspace if it doesn't already exist
                arcpy.CreateDomain_management(
                    in_workspace=output_workspace,
                    domain_name=domain,
                    domain_description=domain,
                    field_type=field_type,
                    domain_type="CODED"
                )

                # Add domain codes and values
                domain_info = from_workspace_domains.get(domain).get("coded_values")

                for code, value in domain_info.items():
                    print(f"\tAdding [{code}: {value}]")
                    arcpy.AddCodedValueToDomain_management(
                        in_workspace=output_workspace,
                        domain_name=domain,
                        code=code,
                        code_description=value
                    )

            else:
                print(f"\t'{domain}' is already in the output workspace!")

    return {"unfound_domains": unfound_domains, "domains": domains}
