import arcpy

import connections
import domains
import utils

from os import getcwd

arcpy.SetLogHistory(False)

CURRENT_DIR = getcwd()

"""
    LND_outdoor_rec_use
    Field: REC_USE
    Domain: LND_rec_activeusearea_type
    Code/Value: BPK/Bike Park Dirt Jump
    
    LND_park_rec_feature
    Field: MAINRECUSE
    Domain: LND_rec_bike_use
    Code/Value: DIRT JUMP/Dirt Jump
"""

domain_change_info = {
    "LND_rec_activeusearea_type": {
        "BPK": "Pump Tracks"
    },
    "LND_rec_bike_use": {
        "DIRT JUMP": "Pump Tracks"
    }
}

if __name__ == "__main__":
    SCRATCH_GDB = utils.create_fgdb(CURRENT_DIR)

    domains.transfer_domains(
        list(domain_change_info.keys()),
        SCRATCH_GDB,
        from_workspace=connections.prod_rw
    )

    for dbs in [
        [SCRATCH_GDB],
        # connections.dev_connections,
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
