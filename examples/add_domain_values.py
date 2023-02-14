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
    "AST_tree_sp_scien": {
        "CAJA": "Carpinus japonica",
        "CRVI": "Crataegus viridis",
        "FRQU": "Fraxinus quadrangulata",
        "MALO": "Magnolia x loebneri",
        "QUBI": "Quercus bicolor",
        "QUCO": "Quercis coccinea",
        "QUMU": "Quercis muehlenbergii",
        "SAAL": "Sassafras albidium",
        "SO": "Sorbus species",
        "ULAC": "Ulmus x morton"
    },
    "AST_tree_sp_comm": {
        "CAJA": "Japanese Hornbeam",
        "CRVI": "Green Hawthorn",
        "FRQU": "Blue Ash",
        "MALO": "Loebner Magnolia",
        "QUBI": "Swamp White Oak",
        "QUCO": "Scarlet Oak",
        "QUMU": "Chinquapin oak",
        "SAAL": "Sassafras",
        "SO": "Mountain Ash",
        "ULAC": "Accolade elm",
    }
}

if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    for dbs in [
        # [local_gdb],
        [config.get("SERVER", "dev_rw"), config.get("SERVER", "dev_ro"), config.get("SERVER", "dev_web_ro_gdb")],
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
                    prod_sde = config.get("SERVER", "prod_rw") if "APP" in PC_NAME else config.get("SERVER", "prod_rw")

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
                for count, code_value in enumerate(add_code_values, start=1):
                    new_code = code_value
                    new_value = add_code_values[code_value]
                    
                    print(f"{count}/{len(add_code_values)})")
                    domains.add_code_value(db, domain, new_code, new_value)
