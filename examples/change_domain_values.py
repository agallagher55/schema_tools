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
    "TRN_RDM_RoadClosureEditors": {
        "Jason Beanlands": "Jason Beanlands",
    },
}

REMOVE_CODE_VALUES = {
    "TRN_RDM_RoadClosureEditors": ["Martin Brien", ],
    "TRN_RDM_RoadClosureApprover": ["Matt Hamer", ]
    }


if __name__ == "__main__":
    local_gdb = utils.create_fgdb(CURRENT_DIR)

    PC_NAME = environ['COMPUTERNAME']
    run_from = "SERVER" if "APP" in PC_NAME else "LOCAL"

    print(f"\nPC Name: {PC_NAME}\n\tRunning from: {run_from}...")

    local_gdb = utils.create_fgdb(out_folder_path=CURRENT_DIR, out_name="scratch.gdb")

    for dbs in [
        # [local_gdb, ],
        [
            config.get("SERVER", "dev_rw"),
            config.get("SERVER", "dev_ro"),
            config.get("SERVER", "dev_web_ro_gdb"),
        ],
        # [
        # config.get("SERVER", "qa_rw"),  # qa_ro, qa_web_ro will get copied to db when processing rw
        #     config.get("SERVER", "qa_web_ro_gdb"),
        # ],
        # [
        #     config.get("SERVER", "prod_rw"),  # qa_ro, qa_web_ro will get copied to db when processing rw
            #     config.get("SERVER", "prod_web_ro_gdb"),
        # ],

    ]:

        if dbs:
            print(f"\nProcessing dbs: {', '.join(dbs)}...")

            for db in dbs:
                print(f"\nDATABASE: {db}")

                if db == local_gdb:

                    # Check for domains in local workspace
                    required_domains = set(list(ADD_CODE_VALUES.keys()) + list(REMOVE_CODE_VALUES.keys()))
                    domain_present, unfound_domains = domains.domains_in_db(local_gdb, required_domains)

                    if unfound_domains:
                        prod_sde = config.get("SERVER", "prod_rw") if "APP" in PC_NAME else config.get("LOCAL", "prod_rw")

                        domains.transfer_domains(
                            unfound_domains,
                            local_gdb,
                            from_workspace=prod_sde
                        )

                for domain in REMOVE_CODE_VALUES:

                    remove_codes = REMOVE_CODE_VALUES[domain]

                    for count, domain_code in enumerate(remove_codes, start=1):
                        domains.remove_code_value(db, domain, domain_code)

                for domain in ADD_CODE_VALUES:
                    print(f"\tDOMAIN: {domain}")

                    # Check that domain is found in database connection
                    domain_found, db_domains = domains.domains_in_db(db, [domain])

                    if not domain_found:
                        raise ValueError(f"Did not find domain '{domain}' in db. Found domains: {', '.join(db_domains)}")

                    add_code_values = ADD_CODE_VALUES[domain]
                    for count, code_value in enumerate(add_code_values, start=1):
                        new_value = add_code_values[code_value]

                        print(f"\n{count}/{len(add_code_values)}) Domain and Code: {code_value} & {new_value}")
                        domains.add_code_value(db, domain, code_value, new_value)
