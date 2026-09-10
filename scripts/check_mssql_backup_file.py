from dataclasses import replace

from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


BACKUP_FILE = (
    r"G:\Backup\MSSQL\Backup\ESG-Beszamolo-260902"
)


config = SqlServerConfig.from_environment()

master_config = replace(
    config,
    database="master",
)

connection_factory = SqlServerConnectionFactory(
    master_config
)

connection = connection_factory.connect()

connection.autocommit = True

try:
    cursor = connection.cursor()

    print()
    print("BACKUP VERIFYONLY")
    print("=" * 70)

    cursor.execute(
        f"""
        RESTORE VERIFYONLY
        FROM DISK = N'{BACKUP_FILE}'
        """
    )

    while cursor.nextset():
        pass

    print("VERIFYONLY: SIKERES")

    print()
    print("BACKUP FILELISTONLY")
    print("=" * 70)

    cursor.execute(
        f"""
        RESTORE FILELISTONLY
        FROM DISK = N'{BACKUP_FILE}'
        """
    )

    columns = [
        column[0]
        for column in cursor.description
    ]

    rows = cursor.fetchall()

    for row in rows:
        data = dict(
            zip(
                columns,
                row,
            )
        )

        print()
        print(
            "LogicalName:",
            data.get("LogicalName"),
        )
        print(
            "PhysicalName:",
            data.get("PhysicalName"),
        )
        print(
            "Type:",
            data.get("Type"),
        )

    print()
    print("=" * 70)
    print(
        "ADATBÁZIS-MÓDOSÍTÁS: 0 rekord"
    )

finally:
    connection.close()