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

connection_factory = SqlServerConnectionFactory(
    master_config
)

connection = connection_factory.connect()

try:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            ORIGINAL_LOGIN() AS original_login,
            SUSER_SNAME() AS login_name,
            IS_SRVROLEMEMBER('sysadmin') AS is_sysadmin,
            IS_SRVROLEMEMBER('dbcreator') AS is_dbcreator,
            HAS_PERMS_BY_NAME(
                NULL,
                'SERVER',
                'CREATE ANY DATABASE'
            ) AS can_create_database
        """
    )

    row = cursor.fetchone()

    print()
    print("MSSQL RESTORE / CREATE JOGOSULTSÁG")
    print("=" * 70)
    print("Login:", row[1])
    print("sysadmin:", row[2])
    print("dbcreator:", row[3])
    print(
        "CREATE ANY DATABASE:",
        row[4],
    )
    print()
    print("ADATBÁZIS-MÓDOSÍTÁS: 0 rekord")

finally:
    connection.close()