import arcpy

import connections
import domains
import utils

from configparser import ConfigParser

from os import getcwd

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')

CURRENT_DIR = getcwd()

domain_change_info = {
    "AST_amenity_assetcode": {
        "DBD": "Dog Bag Dispenser"
    },
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    domains.transfer_domains(
        list(domain_change_info.keys()),
        local_gdb,
        from_workspace=connections.prod_rw
    )

    for dbs in [
        [local_gdb],
        # connections.dev_connections,
        # [config.get("SERVER", "dev_rw")],
        # [config.get("SERVER", "qa_rw")],
        [config.get("SERVER", "prod_rw")],
        # connections.qa_connections,
        # connections.prod_connections
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            for domain in domain_change_info:
                print(f"\tDOMAIN: {domain}")

                # Check that domain is found in database connection
                domain_found, db_domains = domains.domains_in_db(db, [domain])

                if not domain_found:
                    raise ValueError(f"Did not find domain '{domain}' in db. Found domains: {', '.join(db_domains)}")

                add_code_values = domain_change_info[domain]
                for code_value in add_code_values:
                    new_code = code_value
                    new_value = add_code_values[code_value]

                    domains.add_code_value(db, domain, new_code, new_value)
