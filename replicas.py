import arcpy

RW_SDE = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\DEV_RW_sdeadm.sde"
RO_SDE = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\DEV_RO_sdeadm.sde"

# Synchronize
# Unregister both replicas
# Add feature to RW
    # Version, GlobalIDs

# Copy to RO
# Register as versioned in RO??

# Create replica


def sync_replicas(replica_name, rw_sde, ro_sde):
    print(f"\nSynchronizing changes between replicas, '{replica_name}'...")
    arcpy.SynchronizeChanges_management(
        geodatabase_1=rw_sde,
        in_replica=replica_name,
        geodatabase_2=ro_sde,
        in_direction="FROM_GEODATABASE1_TO_2",
        conflict_policy="IN_FAVOR_OF_GDB1",
        conflict_definition="BY_OBJECT",
        reconcile="RECONCILE"
    )


def add_to_replica(replica_name, rw_sde, ro_sde, replica_features: list):
    """
    - Unregister if replica already exists
    - Add feature(s) to replica
    :param replica_name:
    :param rw_sde:
    :param ro_sde:
    :return:
    """

    with arcpy.EnvManager(workspace=rw_sde):
        sde_replica_name = f"SDEADM.{replica_name}"

        # Check if replica with the same name already exists
        curr_workspace_replicas = [x for x in arcpy.da.ListReplicas(rw_sde)]

        replica_exists = sde_replica_name in [x.name for x in curr_workspace_replicas]
        print(f"Replica already exists? {replica_exists}")

        if replica_exists:

            # Get list of features ALREADY in the replica
            curr_replica = [x for x in curr_workspace_replicas if x.name == sde_replica_name][0]
            curr_replica_features = curr_replica.datasets

            # Add features already in replica to list of features given to the user
            replica_features = curr_replica_features + replica_features

            for db in rw_sde, ro_sde:

                try:
                    # Synchronize replicas
                    sync_replicas(replica_name, rw_sde, ro_sde)

                    print(f"\tUnregistering replica '{sde_replica_name}' from {db}...")
                    arcpy.UnregisterReplica_management(
                        db,
                        sde_replica_name
                    )

                except arcpy.ExecuteError as e:
                    print(e)

        print(f"Creating replica: '{sde_replica_name}' with features: {', '.join(replica_features)}...'")

        arcpy.CreateReplica_management(
            in_data=replica_features,
            in_type="ONE_WAY_REPLICA",
            out_geodatabase=ro_sde,
            out_name=replica_name,
            access_type="FULL",
            initial_data_sender="PARENT_DATA_SENDER",
            expand_feature_classes_and_tables="USE_DEFAULTS",
            reuse_schema="DO_NOT_REUSE",  # This parameter is only available for checkout replicas.
            get_related_data="GET_RELATED",
            geometry_features=None,
            archiving="DO_NOT_USE_ARCHIVING",
            register_existing_data="REGISTER_EXISTING_DATA",  # Specifies whether existing data in the child geodatabase will be used to define the replica datasets. The datasets in the child geodatabase must have the same names as the datasets in the parent geodatabase.
            out_type="GEODATABASE",
            out_xml=None
            )

# Check versioning (traditional) of feature in RW


if __name__ == "__main__":
    replica_name = "replica_testing"
    # replica_features = ["SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas"]

    features = [
        "SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas",  # already in RO
        "SDEADM.LND_subdiv_applications"
    ]

    # add_to_replica(replica_name, RW_SDE, RO_SDE, ["SDEADM.LND_charge_areas", "SDEADM.LND_special_planning_areas"])
    add_to_replica(replica_name, RW_SDE, RO_SDE, ["SDEADM.LND_subdiv_applications"])
