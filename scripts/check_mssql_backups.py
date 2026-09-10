from dataclasses import replace

from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


config = SqlServerConfig.from_environment()

master_config = replace(
    config,
    database="master",
)

connection_factory = (
    SqlServerConnectionFactory(
        master_config
    )
)

connection = connection_factory.connect()

try:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT TOP (10)
            bs.backup_start_date,
            bs.backup_finish_date,
            bs.type,
            bs.database_name,
            bs.backup_size,
            bs.compressed_backup_size,
            bmf.device_type,
            bs.is_copy_only,
            bmf.physical_device_name
        FROM msdb.dbo.backupset AS bs
        INNER JOIN msdb.dbo.backupmediafamily AS bmf
            ON bs.media_set_id = bmf.media_set_id
        WHERE bs.database_name = ?
          AND bs.type = 'D'
        ORDER BY
            bs.backup_finish_date DESC
        """,
        "ESG-Beszamolo",
    )

    rows = cursor.fetchall()

    print()
    print("ESG-BESZAMOLO TELJES BACKUPOK")
    print("=" * 90)

    if not rows:
        print(
            "Nem található teljes backup "
            "az msdb backup history-ban."
        )

    for row in rows:
        print()
        print(
            "Backup kezdete:",
            row[0],
        )
        print(
            "Backup vége:",
            row[1],
        )
        print(
            "Típus:",
            row[2],
        )
        print(
            "Adatbázis:",
            row[3],
        )
        print(
            "Méret:",
            row[4],
        )
        print(
            "Tömörített méret:",
            row[5],
        )
        print(
            "Device type:",
            row[6],
        )
        print(
            "Copy only:",
            row[7],
        )
        print(
            "Fájl / device:",
            row[8],
        )

finally:
    connection.close()