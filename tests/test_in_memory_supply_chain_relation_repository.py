import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.in_memory_supply_chain_relation_repository import InMemorySupplyChainRelationRepository

def _create_requester() -> Company:
    return Company(
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )


def _create_supplier(
    *,
    tax_number: str = "22222222-2-41",
) -> Supplier:
    return Supplier(
        name="Beszállító Kft.",
        tax_number=tax_number,
        country="HU",
    )


def test_repository_adds_relation():
    repository = (InMemorySupplyChainRelationRepository())

    relation = SupplyChainRelation(
        requester=_create_requester(),
        supplier=_create_supplier(),
    )

    result = repository.add(relation)

    assert result is relation

    assert (repository.list_all() == (relation,))


def test_repository_gets_relation_by_id():
    repository = (InMemorySupplyChainRelationRepository())

    relation = SupplyChainRelation(
        requester=_create_requester(),
        supplier=_create_supplier(),
    )

    repository.add(relation)

    assert (repository.get_by_id(relation.relation_id)is relation)


def test_repository_gets_relation_by_parties():
    repository = (InMemorySupplyChainRelationRepository())

    requester = _create_requester()
    supplier = _create_supplier()

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    repository.add(relation)

    assert (
        repository.get_by_parties(
            requester=requester,
            supplier=supplier,
        )
        is relation
    )


def test_repository_rejects_duplicate_parties():
    repository = (InMemorySupplyChainRelationRepository())

    requester = _create_requester()
    supplier = _create_supplier()

    repository.add(SupplyChainRelation(
            requester=requester,
            supplier=supplier,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "relation between requester "
            "and supplier already exists"
        ),
    ):
        repository.add(
            SupplyChainRelation(
                requester=requester,
                supplier=supplier,
            )
        )


def test_repository_allows_supplier_for_multiple_requesters():
    repository = (InMemorySupplyChainRelationRepository())

    requester_1 = Company(
        name="Első Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )

    requester_2 = Company(
        name="Második Zrt.",
        tax_number="33333333-2-41",
        country="HU",
    )

    supplier = _create_supplier()

    relation_1 = SupplyChainRelation(
        requester=requester_1,
        supplier=supplier,
    )

    relation_2 = SupplyChainRelation(
        requester=requester_2,
        supplier=supplier,
    )

    repository.add(relation_1)

    repository.add(relation_2)

    assert (repository.list_for_supplier( supplier) == (
            relation_1,
            relation_2,
        )
    )


def test_repository_lists_relations_for_requester():
    repository = (InMemorySupplyChainRelationRepository())

    requester = _create_requester()

    supplier_1 = _create_supplier(
        tax_number="22222222-2-41"
    )

    supplier_2 = _create_supplier(
        tax_number="33333333-2-41"
    )

    relation_1 = SupplyChainRelation(
        requester=requester,
        supplier=supplier_1,
    )

    relation_2 = SupplyChainRelation(
        requester=requester,
        supplier=supplier_2,
    )

    repository.add(relation_1)

    repository.add(relation_2)

    assert ( repository.list_for_requester(requester) == (
            relation_1,
            relation_2,
        )
    )
def test_repository_removes_relation():
    repository = (
        InMemorySupplyChainRelationRepository()
    )

    relation = SupplyChainRelation(
        requester=_create_requester(),
        supplier=_create_supplier(),
    )

    repository.add(
        relation
    )

    removed = repository.remove(
        relation.relation_id
    )

    assert removed is relation

    assert (
        repository.list_all()
        == ()
    )

    assert (
        repository.get_by_id(
            relation.relation_id
        )
        is None
    )


def test_repository_rejects_removing_unknown_relation():
    repository = (
        InMemorySupplyChainRelationRepository()
    )

    with pytest.raises(
        ValueError,
        match="relation does not exist",
    ):
        repository.remove(
            "unknown-relation-id"
        )