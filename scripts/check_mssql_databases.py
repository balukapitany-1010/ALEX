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
        SELECT
            name,
            state_desc
        FROM sys.databases
        WHERE name LIKE '%ESG%'
           OR name LIKE '%ALEX%'
        ORDER BY name
        """
    )

    print()
    print("ELÉRHETŐ ESG / ALEX ADATBÁZISOK")
    print("=" * 70)

    for row in cursor.fetchall():
        print(
            f"{row[0]} | {row[1]}"
        )

    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")

finally:
    connection.close()