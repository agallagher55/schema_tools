from replicas import replicas

if __name__ == "__main__":
    import LND_ROsde

    # 1. Synchronize
    # 2. Unregister both replicas
    # 3. Copy versioned feature with GlobalIDs to RO
    # 4. Sync replicas, recreate replicas with new feature
    # 5. Add indices

    DEV_RW_SDE = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\DEV_RW_sdeadm.sde"
    DEV_RO_SDE = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\dev_RO_sdeadm.sde"

    dev_rw_workpace = replicas.Workspace(DEV_RW_SDE)

    PROD_RW_SDE = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\prod_RW_sdeadm.sde"
    PROD_RO_SDE = r"C:\Users\gallaga\AppData\Roaming\Esri\ArcGISPro\Favorites\prod_RO_sdeadm.sde"

    # Currently in prod, but not dev --> SNF_Rosde
    replica_name = 'SDEADM.LND_Rosde'

    # Get datasets in replica 'SDEADM.LND_Rosde'
    lnd_replica = replicas.Replica(replica_name, DEV_RW_SDE)
    lnd_datasets = lnd_replica.datasets

    # SYNC
    # Test by making change in rw db --> (LND_GRASS_CONTRACT)
    # sync_replicas(replica_name, DEV_RW_SDE, DEV_RO_SDE)

    # replica_name = "replica_testing"
    # replica_features = ["SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas"]

    features = [
        "SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas",  # already in RO
        "SDEADM.LND_subdiv_applications"
    ]

    replicas.add_to_replica(replica_name, DEV_RW_SDE, DEV_RO_SDE, ["SDEADM.TRN_traffic_calming_assessment"])
    # add_to_replica(replica_name, DEV_RW_SDE, DEV_RO_SDE, LND_ROsde.features)

    # add_to_replica(replica_name, RW_SDE, RO_SDE, ["SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas"])
    # add_to_replica(replica_name, RW_SDE, RO_SDE, ["SDEADM.LND_subdiv_applications"])

    # TODO: Test adding new features to existing replica
    # TODO: Test syncing changes before adding new features
