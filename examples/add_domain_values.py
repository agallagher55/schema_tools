import arcpy

import connections
import domains
import utils

from os import getcwd

arcpy.SetLogHistory(False)

CURRENT_DIR = getcwd()

DOMAIN_NAME = "AAA_operator_asset"
ADD_CODE_VALUES = {
    "ME24191": "Melanie Parker",
}

if __name__ == "__main__":
    SCRATCH_GDB = utils.create_fgdb(CURRENT_DIR)

    # operator_domain = domains.transfer_domains([DOMAIN_NAME, ], SCRATCH_GDB, connections.prod_rw)

    for dbs in [
        # [SCRATCH_GDB]
        connections.dev_connections,
        # connections.qa_connections,
        # connections.prod_connections
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\n\tDatabase: {db}")

            # Check that domain is found in database connection
            domain_found, db_domains = domains.domains_in_db(db, [DOMAIN_NAME])

            if not domain_found:
                raise ValueError(f"Did not find domain '{DOMAIN_NAME}' in db. Found domains: {', '.join(db_domains)}")

            for code_value in ADD_CODE_VALUES:
                new_code = code_value
                new_value = ADD_CODE_VALUES[code_value]

                domains.add_code_value(db, DOMAIN_NAME, new_code, new_value)
