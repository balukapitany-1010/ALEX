from datetime import datetime
from unittest.mock import MagicMock
import pytest
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.repositories.mssql_supplier_registration_repository import MssqlSupplierRegistrationRepository
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


def _create_requester():
    return Company.rehydrate(
        company_key="REQ_11111111241",
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
        created_at=datetime(
            2026,
            1,
            1,
        ),
        updated_at=None,
    )

def test_registration_creates_company_and_relation():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.side_effect = [
        ("REQ_11111111241",),

        None,

        None,

        (
            900,
            "active",
            datetime(
                2026,
                9,
                3,
                10,
                0,
            ),
            datetime(
                2026,
                9,
                3,
                10,
                0,
            ),
        ),
    ]

    repository = (MssqlSupplierRegistrationRepository(factory))
    supplier = Supplier(
        name="Új Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )
    relation = repository.register(
        requester=_create_requester(),
        supplier=supplier,
    )
    assert relation.relation_id == "900"
    assert (relation.supplier is supplier)
    assert (relation.relation_status == "active")
    assert cursor.execute.call_count == 5
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

def test_registration_reuses_existing_company():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    existing_created_at = datetime(
        2026,
        5,
        1,
        9,
        0,
    )

    cursor.fetchone.side_effect = [
        ("REQ_11111111241",),

        (
            "COM_22222222241",
            "Meglévő Cég Kft.",
            "22222222-2-41",
            "HU",
            existing_created_at,
            None,
        ),
        None,
        (
            901,
            "active",
            datetime(
                2026,
                9,
                3,
                10,
                0,
            ),
            datetime(
                2026,
                9,
                3,
                10,
                0,
            ),
        ),
    ]
    repository = (MssqlSupplierRegistrationRepository(factory))
    supplier = Supplier(
        name="Másik beírt név",
        tax_number="22222222-2-41",
        country="HU",
    )
    relation = repository.register(
        requester=_create_requester(),
        supplier=supplier,
    )
    assert (relation.supplier.company_key == "COM_22222222241")
    assert (relation.supplier.name == "Meglévő Cég Kft.")
    assert cursor.execute.call_count == 4
    connection.commit.assert_called_once()

def test_registration_rejects_duplicate_relation():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.side_effect = [
        ("REQ_11111111241",),

        (
            "COM_22222222241",
            "Beszállító Kft.",
            "22222222-2-41",
            "HU",
            datetime(
                2026,
                1,
                1,
            ),
            None,
        ),

        (123,),
    ]
    repository = (MssqlSupplierRegistrationRepository(factory))
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )
    with pytest.raises(
        ValueError,
        match=(
            "relation between requester "
            "and supplier already exists"
        ),
    ):
        repository.register(
            requester=_create_requester(),
            supplier=supplier,
        )
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()

def test_registration_rolls_back_on_database_error():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchone.side_effect = [("REQ_11111111241",),None,]
    cursor.execute.side_effect = [
        None,
        None,
        RuntimeError(
            "database error"
        ),
    ]
    repository = (MssqlSupplierRegistrationRepository(factory))
    supplier = Supplier(
        name="Új Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )
    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        repository.register(
            requester=_create_requester(),
            supplier=supplier,
        )

    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()