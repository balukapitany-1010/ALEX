import pytest

from alex.infrastructure.database.sql_server_config import (
    SqlServerConfig,
)


def test_sql_server_config_reads_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "ALEX_DB_SERVER",
        "TEST-SQL",
    )

    monkeypatch.setenv(
        "ALEX_DB_DATABASE",
        "ALEX_TEST",
    )

    monkeypatch.setenv(
        "ALEX_DB_USERNAME",
        "alex-user",
    )

    monkeypatch.setenv(
        "ALEX_DB_PASSWORD",
        "secret",
    )

    config = (
        SqlServerConfig.from_environment()
    )

    assert config.server == "TEST-SQL"
    assert config.database == "ALEX_TEST"
    assert config.username == "alex-user"
    assert config.password == "secret"

    assert (
        config.driver
        == "ODBC Driver 18 for SQL Server"
    )


def test_sql_server_config_requires_server(
    monkeypatch,
):
    monkeypatch.delenv(
        "ALEX_DB_SERVER",
        raising=False,
    )

    monkeypatch.setenv(
        "ALEX_DB_DATABASE",
        "ALEX_TEST",
    )

    monkeypatch.setenv(
        "ALEX_DB_USERNAME",
        "alex-user",
    )

    monkeypatch.setenv(
        "ALEX_DB_PASSWORD",
        "secret",
    )

    with pytest.raises(
        ValueError,
        match="ALEX_DB_SERVER is required",
    ):
        SqlServerConfig.from_environment()


def test_sql_server_config_requires_database(
    monkeypatch,
):
    monkeypatch.setenv(
        "ALEX_DB_SERVER",
        "TEST-SQL",
    )

    monkeypatch.delenv(
        "ALEX_DB_DATABASE",
        raising=False,
    )

    monkeypatch.setenv(
        "ALEX_DB_USERNAME",
        "alex-user",
    )

    monkeypatch.setenv(
        "ALEX_DB_PASSWORD",
        "secret",
    )

    with pytest.raises(
        ValueError,
        match="ALEX_DB_DATABASE is required",
    ):
        SqlServerConfig.from_environment()