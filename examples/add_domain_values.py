import arcpy

import domains
import utils

from configparser import ConfigParser

from os import getcwd, environ

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

config = ConfigParser()
config.read('config.ini')


CURRENT_DIR = getcwd()

domain_change_info = {
    "AST_tree_dbh": {
        1: "0 to 7 cm",
        2: "7 to 15 cm",
        3: "15 to 30 cm",
        4: "30 to 45 cm",
        5: "45 to 60 cm",
        6: "60 to 76 cm",
        7: "76 to 90 cm",
        8: "90 to 106 cm",
        9: ">106 cm"
    },
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    for dbs in [
        [local_gdb],
        # [config.get("SERVER", "dev_rw"), config.get("SERVER", "dev_ro"), config.get("SERVER", "dev_web_ro_gdb")],
        # [config.get("SERVER", "qa_rw")],
        # [config.get("SERVER", "prod_rw")],
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db == local_gdb:

                # Check for domains in local workspace
                domain_present, unfound_domains = domains.domains_in_db(local_gdb, list(domain_change_info.keys()))

                if unfound_domains:
                    PC_NAME = environ['COMPUTERNAME']
                    prod_sde = config.get("SERVER", "prod_rw") if "APP" in PC_NAME else config.get("LOCAL", "prod_rw")

                    domains.transfer_domains(
                        list(domain_change_info.keys()),
                        local_gdb,
                        from_workspace=prod_sde
                    )

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
