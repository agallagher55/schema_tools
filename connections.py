import arcpy


def prevent_connections(sde):
    import time

    with arcpy.EnvManager(workspace=sde):
        # Block new connections to the database.
        try:
            print(f'Blocking connections in {sde}...')
            arcpy.AcceptConnections(sde, accept_connections=False)

        except(arcpy.ExecuteError, arcpy.ExecuteWarning) as e:
            print(e)
            print('Blocked all connections')

        time.sleep(60)  # wait 60 seconds

        # Disconnect all users from the database.
        try:
            print(f'Disconnecting all users from {sde}...')
            arcpy.DisconnectUser(sde, users="ALL")

        except(arcpy.ExecuteError, arcpy.ExecuteWarning) as e:
            print(e)
            print('Disconnected all users')


def allow_connections(sde):
    # Allow the database to begin accepting connections again
    try:
        print(f'Accepting Connections from {sde}...')
        arcpy.AcceptConnections(sde, accept_connections=True)

    except(arcpy.ExecuteError, arcpy.ExecuteWarning) as e:
        print(e)


def check_connections(db_connections: [[]]):
    # Make sure all db connection files are valid
    print(f"\nChecking connections...")

    fails = []
    success = []

    for connections in db_connections:
        for connection in connections:

            if not arcpy.Exists(connection):
                fails.append(connection)

            else:
                success.append(connection)

    if fails:
        raise IndexError(f"Invalid connection(s) found: {', '.join(fails)}")

    return {"valid_connections": success}


def connection_type(db: str) -> (str, str):
    """
    Determine the type and read-write status of a database.

    This function takes in a database name and prints a message indicating the type and read-write status of the database. It returns a tuple containing the type and read-write status of the database.

    Input:
    db (str): A string representing the name of a database.

    Output:
    A tuple containing the type and read-write status of the database. The type can be "SDE" or "GDB", and the read-write status can be "RW" or "RO". If the database type or read-write status cannot be determined, the corresponding value in the tuple will be an empty string.

    Examples:
    connection_type("RW_SDEADM") -> ("SDE", "RW")
    connection_type("RO_SDEADM") -> ("SDE", "RO")
    connection_type("database.gdb") -> ("GDB", "")
    """

    print("\nAnalyzing database type...")

    db = db.upper()

    rw_sde_db = "RW_SDEADM" in db
    ro_sde_db = "RO_SDEADM" in db or (db.endswith(".GDB") and "RO" in db)

    ro_gdb = db.endswith(".GDB") and "RO" in db
    scratch_gdb = db.endswith(".GDB") and "RO" not in db

    if rw_sde_db:
        print(f"\t --> RW SDE")
        return "SDE", "RW"

    elif ro_sde_db:
        print(f"\t --> RO SDE")
        return "SDE", "RO"

    elif ro_gdb:
        print(f"\t --> Local RO")
        return "GDB", "RO"

    elif scratch_gdb:
        print(f"\t --> Local gdb")
        return "GDB", ""

    else:
        print("\t --> *Unclassified db type...")
        return "", ""


if __name__ == "__main__":
    # DEV
    dev_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RW_SDEADM.sde"
    dev_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RO_SDEADM.sde"
    dev_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_DEV_RO.sde"  # Only need to include when adding a new domain to a field?
    dev_gdbs = [dev_ro, dev_rw, dev_web_ro]

    # QA
    qa_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RW_SDEADM.sde"
    qa_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_SDEADM.sde"
    qa_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_webgis.sde"  # Only need to include when adding a new domain to a field?
    qa_gdbs = [qa_rw, qa_ro, qa_web_ro]

    # PROD
    prod_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RW_SDEADM.sde"
    prod_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RO_SDEADM.sde"
    prod_ro_web = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_PROD_RO_win.sde"  # Only need to include when adding a new domain to a field?
    prod_gdbs = [prod_rw, prod_ro, prod_ro_web]

    dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
    qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"
    prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_Prod\fgdbs\web_RO.gdb"

    web_fs_gdbs = [prod_web_ro_gdb, dev_web_ro_gdb, qa_web_ro_gdb]

    # connections = check_connections([
    #     dev_gdbs,
    #     qa_gdbs,
    #     prod_gdbs,
    #     web_fs_gdbs,
    # ]
    # )
