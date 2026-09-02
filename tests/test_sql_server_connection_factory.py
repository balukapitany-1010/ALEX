from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)
from alex.infrastructure.database.sql_server_connection_factory import (
    SqlServerConnectionFactory,
)


def test_factory_builds_connection_string():
    config = SqlServerConfig(
        server="TEST-SQL",
        database="ALEX_TEST",
        username="alex-user",
        password="secret",
    )

    factory = (
        SqlServerConnectionFactory(
            config
        )
    )

    connection_string = (
        factory.build_connection_string()
    )

    assert "SERVER=TEST-SQL;" in connection_string
    assert "DATABASE=ALEX_TEST;" in connection_string
    assert "UID=alex-user;" in connection_string

    assert (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        in connection_string
    )

    assert "Encrypt=yes;" in connection_string

    assert (
        "TrustServerCertificate=yes;"
        in connection_string
    )