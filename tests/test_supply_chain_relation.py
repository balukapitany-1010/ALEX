import pytest
from datetime import datetime, timezone, UTC
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


def test_supply_chaint_relation_connects_and_supplier():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number= "11111111-1-11",
    )

    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-22",
    )
    relation = SupplyChainRelation(
        requester = requester,
        supplier = supplier,
    )
    assert relation.requester is requester
    assert relation.supplier is supplier

def test_supply_chain_relation_rejects_invalid_requester():
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-22",

        )
    with pytest.raises(TypeError):
        SupplyChainRelation(
        requester = "Nem company objektum",
        supplier = supplier,
        )

def test_supply_chain_relation_rejects_invalid_supplier():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number= "11111111-1-11",
    )
    with pytest.raises(TypeError):
        SupplyChainRelation(
            requester = requester,
            supplier = "Nem supplier objektum",
        )

def test_supply_chain_relation_have_unique_ids():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number= "11111111-1-11",
        )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number= "22222222-2-22",
    )
    relation1 = SupplyChainRelation(
        requester = requester,
        supplier = supplier,
    )

    relation2 = SupplyChainRelation(
        requester = requester,
        supplier = supplier,
    )

    assert relation1.relation_id != relation2.relation_id

def test_supply_chain_relation_generates_relation_id():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number= "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number= "22222222-2-22",
    )
    relation = SupplyChainRelation(
        requester = requester,
        supplier = supplier,
    )
    assert relation.relation_id is not None
    assert isinstance(relation.relation_id, str)
    assert len(relation.relation_id) > 0

def test_supply_chain_relation_has_created_at():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    assert relation.created_at is not None
    assert isinstance(relation.created_at, datetime)

def test_relation_can_be_rehydrated():
    requester = Company(
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )

    created_at = datetime(
        2026,
        7,
        1,
        10,
        30,
        tzinfo=UTC,
    )

    updated_at = datetime(
        2026,
        7,
        2,
        11,
        45,
        tzinfo=UTC,
    )

    relation = (
        SupplyChainRelation.rehydrate(
            relation_id=298,
            requester=requester,
            supplier=supplier,
            relation_status="active",
            created_at=created_at,
            updated_at=updated_at,
        )
    )

    assert relation.relation_id == "298"
    assert relation.requester is requester
    assert relation.supplier is supplier

    assert (
        relation.relation_status
        == "active"
    )

    assert (
        relation.created_at
        == created_at
    )

    assert (
        relation.updated_at
        == updated_at
    )


def test_relation_rehydrate_accepts_missing_updated_at():
    requester = Company(
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    relation = (
        SupplyChainRelation.rehydrate(
            relation_id=298,
            requester=requester,
            supplier=supplier,
            relation_status="active",
            created_at=datetime(
                2026,
                7,
                1,
                tzinfo=UTC,
            ),
            updated_at=None,
        )
    )

    assert relation.updated_at is None