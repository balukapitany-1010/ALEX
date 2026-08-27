import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.services.supply_chain_relation_service import (
    SupplyChainRelationService,
)


def test_service_can_create_relation():
    service = SupplyChainRelationService()

    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    relation = service.create_relation(
        requester=requester,
        supplier=supplier,
    )

    assert relation.requester is requester
    assert relation.supplier is supplier


def test_service_lists_relations():
    service = SupplyChainRelationService()

    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    relation = service.create_relation(
        requester=requester,
        supplier=supplier,
    )

    assert service.list_relations() == (
        relation,
    )


def test_service_rejects_duplicate_relation():
    service = SupplyChainRelationService()

    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    service.create_relation(
        requester=requester,
        supplier=supplier,
    )

    with pytest.raises(
        ValueError,
        match=(
            "relation between requester "
            "and supplier already exists"
        ),
    ):
        service.create_relation(
            requester=requester,
            supplier=supplier,
        )


def test_same_supplier_can_belong_to_multiple_requesters():
    service = SupplyChainRelationService()

    requester1 = Company(
        name="Első Cég Kft.",
        tax_number="11111111-2-41",
    )

    requester2 = Company(
        name="Második Cég Kft.",
        tax_number="22222222-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="33333333-2-41",
    )

    relation1 = service.create_relation(
        requester=requester1,
        supplier=supplier,
    )

    relation2 = service.create_relation(
        requester=requester2,
        supplier=supplier,
    )

    assert relation1 is not relation2

    assert len(
        service.list_relations_for_supplier(
            supplier
        )
    ) == 2


def test_service_lists_relations_for_requester():
    service = SupplyChainRelationService()

    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier1 = Supplier(
        name="Első Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    supplier2 = Supplier(
        name="Második Beszállító Kft.",
        tax_number="33333333-2-41",
    )

    relation1 = service.create_relation(
        requester=requester,
        supplier=supplier1,
    )

    relation2 = service.create_relation(
        requester=requester,
        supplier=supplier2,
    )

    assert service.list_relations_for_requester(
        requester
    ) == (
        relation1,
        relation2,
    )