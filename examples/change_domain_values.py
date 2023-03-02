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

ADD_CODE_VALUES = {
    "LND_zoning_HPSBB": {
        "R-1B": "R-1B",
        "R-1C": "R-1C",
    },

}

REMOVE_CODE_VALUES = {
    "LND_zoning_HPSBB":
        {
            "R-1b": "R-1b"
        },
    }


if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    for dbs in [
        # [local_gdb],
        # [config.get("SERVER", "dev_rw"), config.get("SERVER", "dev_ro"), config.get("SERVER", "dev_web_ro_gdb")],
        # [
        #     config.get("SERVER", "qa_rw"),
        #     config.get("SERVER", "qa_ro"),
        #     config.get("SERVER", "qa_web_ro_gdb")
        # ],
        [config.get("SERVER", "prod_rw"), config.get("SERVER", "prod_ro"), config.get("SERVER", "prod_web_ro_gdb")],
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            if db == local_gdb:

                # Check for domains in local workspace
                domain_present, unfound_domains = domains.domains_in_db(local_gdb, list(ADD_CODE_VALUES.keys()))

                if unfound_domains:
                    PC_NAME = environ['COMPUTERNAME']
                    prod_sde = config.get("SERVER", "prod_rw") if "APP" in PC_NAME else config.get("SERVER", "prod_rw")

                    domains.transfer_domains(
                        list(ADD_CODE_VALUES.keys()),
                        local_gdb,
                        from_workspace=prod_sde
                    )

            for domain in REMOVE_CODE_VALUES:
                remove_codes = list(REMOVE_CODE_VALUES[domain].keys())

                for count, code in enumerate(remove_codes, start=1):
                    domains.remove_code_value(db, domain, code)

            for domain in ADD_CODE_VALUES:
                print(f"\tDOMAIN: {domain}")

                # Check that domain is found in database connection
                domain_found, db_domains = domains.domains_in_db(db, [domain])

                if not domain_found:
                    raise ValueError(f"Did not find domain '{domain}' in db. Found domains: {', '.join(db_domains)}")

                add_code_values = ADD_CODE_VALUES[domain]
                for count, code_value in enumerate(add_code_values, start=1):
                    new_code = code_value.upper()
                    new_value = add_code_values[code_value]

                    print(f"{count}/{len(add_code_values)})")
                    domains.add_code_value(db, domain, new_code, new_value)

# TODO: Unable to remove R-1b from RO due to a lock

