from datetime import UTC, datetime
from unittest.mock import MagicMock
import pytest
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.mssql_supply_chain_relation_repository import MssqlSupplyChainRelationRepository
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

def _create_requester() -> Company:
    return Company(
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )

def _create_supplier() -> Supplier:
    return Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )

def _create_relation_row():
    return (
        298,
        "active",
        datetime(
            2026,
            7,
            1,
            10,
            30,
        ),
        datetime(
            2026,
            7,
            2,
            11,
            45,
        ),

        "REQ_11111111241",
        "Kötelezett Zrt.",
        "11111111-2-41",
        "HU",
        datetime(
            2026,
            6,
            1,
            8,
            0,
        ),
        None,

        "SUP_22222222241",
        "Beszállító Kft.",
        "22222222-2-41",
        "HU",
        datetime(
            2026,
            6,
            2,
            9,
            0,
        ),
        None,
    )

def test_mssql_repository_lists_relations():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = [_create_relation_row()]
    repository = (MssqlSupplyChainRelationRepository(factory))
    relations = repository.list_all()
    assert isinstance(relations, tuple,)
    assert len(relations) == 1
    relation = relations[0]
    assert isinstance(relation, SupplyChainRelation,)
    assert relation.relation_id == "298"
    assert (relation.requester.name == "Kötelezett Zrt.")
    assert (relation.supplier.name == "Beszállító Kft.")
    assert (relation.relation_status == "active")
    assert ( relation.created_at == datetime(
            2026,
            7,
            1,
            10,
            30,
            tzinfo=UTC,
        )
    )
    connection.close.assert_called_once()

def test_mssql_repository_gets_relation_by_id():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = [_create_relation_row()]
    repository = ( MssqlSupplyChainRelationRepository(factory))
    relation = repository.get_by_id("298")
    assert relation is not None
    assert relation.relation_id == "298"
    assert (relation.requester.company_key == "REQ_11111111241")
    assert (relation.supplier.company_key == "SUP_22222222241")
    connection.close.assert_called_once()

def test_mssql_repository_returns_none_for_unknown_id():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = []
    repository = (MssqlSupplyChainRelationRepository(factory))
    result = repository.get_by_id("999999")
    assert result is None
    connection.close.assert_called_once()

def test_mssql_repository_gets_relation_by_parties():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = [_create_relation_row()]
    repository = (MssqlSupplyChainRelationRepository(factory))

    requester = Company.rehydrate(
        company_key="REQ_11111111241",
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
        created_at=datetime(
            2026,
            6,
            1,
        ),
        updated_at=None,
    )

    supplier = Supplier.rehydrate(
        company_key="SUP_22222222241",
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
        created_at=datetime(
            2026,
            6,
            2,
        ),
        updated_at=None,
    )

    relation = repository.get_by_parties(
        requester=requester,
        supplier=supplier,
    )

    assert relation is not None
    assert relation.relation_id == "298"
    connection.close.assert_called_once()

def test_mssql_repository_adds_relation():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    requester = _create_requester()
    supplier = _create_supplier()

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    repository = (MssqlSupplyChainRelationRepository(factory))
    repository.get_by_parties = MagicMock(return_value=None)
    cursor.fetchone.return_value = (
        901,
        "active",
        datetime(
            2026,
            9,
            3,
            8,
            30,
        ),
        datetime(
            2026,
            9,
            3,
            8,
            30,
        ),
    )
    result = repository.add(relation)
    assert isinstance(result, SupplyChainRelation,)
    assert result.relation_id == "901"
    assert result.requester is requester
    assert result.supplier is supplier
    assert (result.relation_status == "active")
    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()


def test_mssql_repository_rejects_duplicate_relation():
    factory = _create_factory()

    requester = _create_requester()
    supplier = _create_supplier()

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    repository = (MssqlSupplyChainRelationRepository(factory))
    repository.get_by_parties = MagicMock(return_value=relation)

    with pytest.raises(
        ValueError,
        match=(
            "relation between requester "
            "and supplier already exists"
        ),
    ):
        repository.add(relation)
    factory.connect.assert_not_called()

def test_mssql_repository_rolls_back_when_add_fails():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.execute.side_effect = (RuntimeError("database error"))
    requester = _create_requester()
    supplier = _create_supplier()
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    repository = (MssqlSupplyChainRelationRepository(factory))
    repository.get_by_parties = MagicMock(return_value=None)

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        repository.add(relation)
    connection.commit.assert_not_called()
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()

def test_mssql_repository_lists_relations_for_requester():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = [_create_relation_row()]
    repository = ( MssqlSupplyChainRelationRepository(factory))
    requester = Company.rehydrate(
        company_key="REQ_11111111241",
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
        created_at=datetime(
            2026,
            6,
            1,
        ),
        updated_at=None,
    )

    relations = (repository.list_for_requester(requester))
    assert len(relations) == 1
    assert (relations[0].requester.company_key == "REQ_11111111241")

def test_mssql_repository_lists_relations_for_supplier():
    factory = _create_factory()
    connection = MagicMock()
    cursor = MagicMock()
    connection.cursor.return_value = cursor
    factory.connect.return_value = connection
    cursor.fetchall.return_value = [_create_relation_row()]
    repository = (MssqlSupplyChainRelationRepository(factory))

    supplier = Supplier.rehydrate(
        company_key="SUP_22222222241",
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
        created_at=datetime(
            2026,
            6,
            2,
        ),
        updated_at=None,
    )
    relations = (repository.list_for_supplier(supplier))
    assert len(relations) == 1
    assert (relations[0].supplier.company_key == "SUP_22222222241")