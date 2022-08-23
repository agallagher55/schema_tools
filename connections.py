import arcpy


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

    web_fs_gdbs = [prod_web_ro_gdb,dev_web_ro_gdb,qa_web_ro_gdb]

    connections = check_connections([
        dev_gdbs,
        qa_gdbs,
        prod_gdbs,
        web_fs_gdbs,
    ]
    )