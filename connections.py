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

    print(f"\nAnalyzing database type for {db}...")

    db = db.upper()

    rw_sde_db = "RW_SDEADM" in db
    ro_sde_db = "RO_SDEADM" in db or (db.endswith(".GDB") and "RO" in db)

    ro_gdb = db.endswith(".GDB") and "RO" in db
    scratch_gdb = db.endswith(".GDB") and "RO" not in db

    if rw_sde_db:
        print(f"\tDatabase Type: RW SDE")
        return "SDE", "RW"

    elif ro_sde_db:
        print(f"\tDatabase Type: RO SDE")
        return "SDE", "RO"

    elif ro_gdb:
        print(f"\tDatabase Type: Local RO")
        return "GDB", "RO"

    elif scratch_gdb:
        print(f"\tDatabase Type: Local gdb")
        return "GDB", ""

    else:
        print("\tDatabase Type: *Unclassified.")
        return "", ""


if __name__ == "__main__":
    db = "Geodatabase.gdb"
    db_type, db_rights = connection_type(db)
