from unittest.mock import MagicMock
from datetime import datetime
import pytest
from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.mssql_supplier_repository import MssqlSupplierRepository
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

def test_mssql_supplier_repository_adds_supplier():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = None
    repository = MssqlSupplierRepository(factory)
    supplier = Supplier(
        name="Teszt Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )
    result = repository.add(supplier)
    assert result is supplier
    assert (result.company_key == "COM_12345678241")
    assert cursor.execute.call_count == 2
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

def test_mssql_supplier_repository_rejects_existing_company():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = ("COM_12345678241",)
    repository = MssqlSupplierRepository(factory)
    supplier = Supplier(
        name="Teszt Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )

    with pytest.raises(
        ValueError,
        match="company with same",
    ):
        repository.add(supplier)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()


def test_mssql_supplier_repository_rolls_back_when_add_fails():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = None
    cursor.execute.side_effect = [
        None,
        RuntimeError("database error"),
    ]

    repository = MssqlSupplierRepository(factory)
    supplier = Supplier(
        name="Teszt Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )
    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        repository.add(supplier)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()

def test_mssql_supplier_repository_updates_supplier():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = ("COM_12345678241",)
    repository = MssqlSupplierRepository(factory)
    supplier = Supplier.rehydrate(
        company_key="COM_12345678241",
        name="Régi Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
        created_at=datetime(
            2026,
            1,
            1,
        ),
        updated_at=datetime(
            2026,
            1,
            1,
        ),
    )
    supplier.update(
        name="Új Beszállító Kft.",
        country="DE",
    )
    result = repository.update(supplier)
    assert result is supplier
    assert (result.name  == "Új Beszállító Kft.")
    assert result.country == "DE"
    assert cursor.execute.call_count == 2
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

def test_mssql_supplier_repository_rejects_update_for_unknown_supplier():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = None
    repository = MssqlSupplierRepository(factory)
    supplier = Supplier(
        name="Ismeretlen Kft.",
        tax_number="99999999-2-41",
        country="HU",
    )
    with pytest.raises(
        ValueError,
        match="supplier does not exist",
    ):
        repository.update(supplier)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()

def test_mssql_supplier_repository_rolls_back_when_update_fails():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.return_value = ("COM_12345678241",)
    cursor.execute.side_effect = [None,RuntimeError("database error"),]
    repository = MssqlSupplierRepository(factory)
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="12345678-2-41",
        country="HU",
    )
    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        repository.update(supplier)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()