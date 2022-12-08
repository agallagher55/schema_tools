import arcpy

import connections
import domains
import utils

from os import getcwd

arcpy.SetLogHistory(False)

CURRENT_DIR = getcwd()

DOMAIN_NAME = "LND_gflum_DART"
ADD_CODE_VALUES = {
    "CDD": "CDD",
}

# Value needs to be CDD. All other values in GFLUM domain are the same as the code.
# --> The field has a max length of 12 - wouldn't fit full name anyway.

if __name__ == "__main__":
    SCRATCH_GDB = utils.create_fgdb(CURRENT_DIR)

    # operator_domain = domains.transfer_domains([DOMAIN_NAME, ], SCRATCH_GDB, from_workspace=connections.prod_rw)

    for dbs in [
        # [SCRATCH_GDB]
        connections.dev_connections,
        # connections.qa_connections,
        # connections.prod_connections
    ]:

        print(f"\nProcessing dbs: {', '.join(dbs)}...")

        for db in dbs:
            print(f"\nDATABASE: {db}")

            # Check that domain is found in database connection
            domain_found, db_domains = domains.domains_in_db(db, [DOMAIN_NAME])

            if not domain_found:
                raise ValueError(f"Did not find domain '{DOMAIN_NAME}' in db. Found domains: {', '.join(db_domains)}")

            for code_value in ADD_CODE_VALUES:
                new_code = code_value
                new_value = ADD_CODE_VALUES[code_value]

                domains.add_code_value(db, DOMAIN_NAME, new_code, new_value)
