from datetime import UTC, datetime
from unittest.mock import MagicMock
from alex.esg.domain.company import Company
from alex.esg.repositories.mssql_company_repository import MssqlCompanyRepository
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def _create_factory():
    config = SqlServerConfig(
        server="TEST-SQL",
        database="TEST-DB",
        username="test-user",
        password="test-password",
    )
    factory = SqlServerConnectionFactory(config)
    factory.connect = MagicMock()
    return factory

def test_mssql_repository_adds_company():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    repository = MssqlCompanyRepository(factory)

    company = Company(
        name="Teszt Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )
    result = repository.add(company)
    assert result is company
    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

def test_mssql_repository_gets_company_by_key():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    created_at = datetime(
        2026,
        1,
        10,
        12,
        30,
    )
    cursor.fetchone.return_value = (
        "COM_12345678241",
        "Teszt Kft.",
        "12345678-2-41",
        "HU",
        created_at,
        None,
    )
    repository = MssqlCompanyRepository(factory)
    company = repository.get_by_key("COM_12345678241")
    assert company is not None
    assert (company.company_key == "COM_12345678241")
    assert (company.name == "Teszt Kft.")
    assert (company.tax_number == "12345678-2-41")
    assert (company.created_at == created_at.replace(tzinfo=UTC))
    assert company.updated_at is None
    connection.close.assert_called_once()

def test_mssql_repository_returns_none_for_unknown_key():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = None
    repository = MssqlCompanyRepository(factory)
    result = repository.get_by_key("COM_UNKNOWN")
    assert result is None
    connection.close.assert_called_once()

def test_mssql_repository_rolls_back_when_add_fails():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.execute.side_effect = RuntimeError("database error")
    repository = MssqlCompanyRepository(factory)
    company = Company(
        name="Teszt Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )

    try:
        repository.add(company)

    except RuntimeError:
        pass
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()

