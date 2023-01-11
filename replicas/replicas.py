import arcpy

REPLICAS = {
    "TRN_Rosde", "SNF_Rosde", "ROAD_Rosde", "StrDir_Rosde", "MAP_Rosde", "LND_Rosde",
    "EMO_Rosde", "CIV_Rosde", "BLD_LND_Rosde", "AST_Rosde", "ADM_Rosde"
}


class Workspace:
    def __init__(self, source: str):
        self.source = source

        self.replicas = self.replicas()

        if not arcpy.Exists(source):
            raise ValueError(f"Workspace, '{source}' does not exist.")

    def replicas(self):
        print(f"Getting replicas in '{self.source}'...")
        return sorted(arcpy.da.ListReplicas(self.source), key=lambda x: x.name)


class Replica:
    """
    https://pro.arcgis.com/en/pro-app/2.9/arcpy/data-access/replica.htm
    """

    def __init__(self, name: str, workspace: str):
        self.name = name
        self.workspace = workspace

        self.replica = [x for x in arcpy.da.ListReplicas(workspace)][0]
        self.datasets = self.datasets()

    def datasets(self):
        datasets = self.replica.datasets
        return sorted(datasets)


def sync_replicas(replica_name: str, rw_sde: str, ro_sde: str):
    """
    - Sync updates from RW to RO
    :param replica_name:
    :param rw_sde:
    :param ro_sde:
    :return:
    """

    print(f"\nSynchronizing changes between replicas, '{replica_name}'...")
    arcpy.SynchronizeChanges_management(
        geodatabase_1=rw_sde,
        in_replica=replica_name,
        geodatabase_2=ro_sde,
        in_direction="FROM_GEODATABASE1_TO_2",
        conflict_policy="IN_FAVOR_OF_GDB1",
        conflict_definition="BY_OBJECT",
        reconcile="RECONCILE "
    )


def register_as_versioned(feature):
    print(f"\nRegistering {feature} as versioned...")
    arcpy.RegisterAsVersioned_management(feature)
    print(arcpy.GetMessages(2))


def add_to_replica(replica_name: str, rw_sde: str, ro_sde: str, add_features: list, topology_dataset=False):
    """
    - Unregister if replica already exists
    - Add feature(s) to replica
    - Does not check to see if replica_features are already in rw, ro replicas

    :param replica_name:
    :param rw_sde:
    :param ro_sde:
    :return:
    """

    replica_name = replica_name.replace("SDEADM.", "")
    access_type = "SIMPLE"

    if topology_dataset:
        access_type = "FULL"

    print(f"\nAdding {', '.join(add_features)} to replica '{replica_name}'...")

    with arcpy.EnvManager(workspace=ro_sde):
        # Check to see if feature exists in ro workspace

        print(f"Checking to make sure feature exists in {ro_sde}...")
        invalid_ro_features = [x for x in add_features if not arcpy.Exists(x)]

        if invalid_ro_features:
            raise ValueError(f"ERROR: Did not find features ({', '.join(invalid_ro_features)}) in {ro_sde}")

    with arcpy.EnvManager(workspace=rw_sde):
        sde_replica_name = f"SDEADM.{replica_name}"

        # Check to see if feature exists in rw workspace

        print(f"Checking to make sure feature exists in {ro_sde}...")
        invalid_rw_features = [x for x in add_features if not arcpy.Exists(x)]

        if invalid_rw_features:
            raise ValueError(f"ERROR: Did not find features in {rw_sde}: {', '.join(invalid_rw_features)}")

        # Check if replica with the same name already exists
        print(f"Checking if replica already exists...")
        rw_replicas = [x for x in arcpy.da.ListReplicas(rw_sde)]

        replica_exists = sde_replica_name in [x.name for x in rw_replicas]
        print(f"\tReplica already exists? {replica_exists}")

        # Check if add_features are versioned
        for feature in add_features:
            desc = arcpy.Describe(feature)
            versioned = desc.isVersioned

            if not versioned:
                register_as_versioned(feature)

        if replica_exists:
            # Synchronize replicas to update RO feature(s)
            sync_replicas(replica_name, rw_sde, ro_sde)

            # Get list of features ALREADY in the replica
            rw_replica = [x for x in rw_replicas if x.name == sde_replica_name][0]
            curr_replica_features = rw_replica.datasets

            # Add features already in replica to list of features given to the user
            add_features = sorted(list(set(curr_replica_features + add_features)))

            # Unregister rw, ro replicas so they can be recreated with additional features
            for db in rw_sde, ro_sde:
                print(f"\tUnregistering replica '{sde_replica_name}' from {db}...")
                arcpy.UnregisterReplica_management(
                    db,
                    sde_replica_name
                )

        print(f"\nCreating replica: '{sde_replica_name}' with features: {', '.join(add_features)}...'")

        arcpy.CreateReplica_management(
            in_data=add_features,
            in_type="ONE_WAY_REPLICA",
            out_geodatabase=ro_sde,
            out_name=replica_name,
            access_type=access_type,  # FULL: SNF one Full, the rest will be Simple - Complex types (topologies and networks) are supported and the data must be versioned.
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
