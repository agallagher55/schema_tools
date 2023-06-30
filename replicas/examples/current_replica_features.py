"""
Get a dictionary of Oracle replica names and the features in the replicas
--> export to json
"""

import json
import replicas

dev_rw = r"E:\HRM\Scripts\SDE\dev_RW_sdeadm.sde"
dev_ro = r"E:\HRM\Scripts\SDE\dev_RO_sdeadm.sde"

qa_rw = r"E:\HRM\Scripts\SDE\qa_RW_sdeadm.sde"
qa_ro = r"E:\HRM\Scripts\SDE\qa_RO_sdeadm.sde"

prod_rw = r"E:\HRM\Scripts\SDE\prod_RW_sdeadm.sde"
prod_ro = r"E:\HRM\Scripts\SDE\prod_RO_sdeadm.sde"


if __name__ == "__main__":

    sde_workspace = prod_rw

    replica_data = dict()

    for replica in replicas.REPLICAS:
        print(f"\n{replica}")

        try:
            replica_obj = replicas.Replica(replica, sde_workspace)
            replica_features = replica_obj.datasets

            print(f"\t{', '.join(replica_features)}")
            replica_data[replica] = replica_features

        except IndexError as e:
            print(f"Could not find replica in {sde_workspace}")
            continue

    # Export to JSON
    with open(f"replica_oracle_data.json", "w") as jfile:
        json.dump(replica_data, jfile, indent=4)
