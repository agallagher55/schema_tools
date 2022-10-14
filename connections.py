import arcpy


# DEV
dev_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RW_SDEADM.sde"
dev_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\DEV_RO_SDEADM.sde"
dev_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_DEV_RO.sde"  # Only need to include when adding a new domain to a field
dev_web_ro_gdb = r"\\msfs06\GISApp\AGS_Dev\fgdbs\web_RO.gdb"
dev_connections = [
    dev_rw,
    # dev_ro,
    # dev_web_ro,
    # dev_web_ro_gdb
]

qa_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RW_SDEADM.sde"
qa_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_SDEADM.sde"
qa_web_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\QA_RO_webgis.sde"  # Only need to include when adding a new domain to a field
qa_web_ro_gdb = r"\\msfs06\GISApp\AGS_QA\fgdbs\web_RO.gdb"

qa_connections = [
    # qa_ro,
    # qa_web_ro,
    # qa_web_ro_gdb,
    qa_rw,

]


prod_rw = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RW_SDEADM.sde"
prod_ro = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\PROD_RO_SDEADM.sde"
prod_ro_web = "C:\\Users\\gallaga\\AppData\\Roaming\\Esri\\ArcGISPro\\Favorites\\webgis_PROD_RO_win.sde"  # Only need to include when adding a new domain to a field
prod_web_ro_gdb = r"\\msfs06\GISApp\AGS_Prod\fgdbs\web_RO.gdb"

prod_connections = [
    # prod_ro,
    # prod_ro_web,
    # prod_web_ro_gdb,
    prod_rw
]


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


def connection_type(db):
    print("\nAnalyzing database type...")

    rw_sde_db = "RW_SDEADM" in db
    ro_sde_db = "RO_SDEADM" in db or (db.endswith(".gdb") and "RO" in db)

    ro_gdb = db.endswith(".gdb") and "RO" in db
    scratch_gdb = db.endswith(".gdb") and "RO" not in db

    if rw_sde_db:
        print(f"\t --> RW SDE")
        return "SDE", "RW"

    elif ro_sde_db:
        print(f"\t --> RO SDE")
        return "SDE", "RW"

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
