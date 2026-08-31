import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.services.submission_party_resolver import (
    ResolvedSubmissionParties,
)
from alex.esg.services.submission_relation_resolver import (
    SubmissionRelationResolver,
)
from alex.esg.services.supply_chain_relation_service import (
    SupplyChainRelationService,
)


def _create_parties():
    requester = Company(
        name="Kötelezett Zrt.",
        tax_number="22222222-2-41",
        country="HU",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="11111111-2-41",
        country="HU",
    )

    return ResolvedSubmissionParties(
        requester=requester,
        supplier=supplier,
    )


def test_relation_resolver_creates_relation():
    service = SupplyChainRelationService()

    resolver = SubmissionRelationResolver(
        relation_service=service,
    )

    parties = _create_parties()

    relation = resolver.resolve(
        parties
    )

    assert relation.requester is parties.requester
    assert relation.supplier is parties.supplier

    assert len(
        service.list_relations()
    ) == 1


def test_relation_resolver_reuses_existing_relation():
    service = SupplyChainRelationService()

    parties = _create_parties()

    existing = service.create_relation(
        requester=parties.requester,
        supplier=parties.supplier,
    )

    resolver = SubmissionRelationResolver(
        relation_service=service,
    )

    resolved = resolver.resolve(
        parties
    )

    assert resolved is existing

    assert len(
        service.list_relations()
    ) == 1


def test_relation_resolver_keeps_different_suppliers_separate():
    service = SupplyChainRelationService()

    parties1 = _create_parties()

    supplier2 = Supplier(
        name="Másik Beszállító Kft.",
        tax_number="33333333-2-41",
        country="HU",
    )

    parties2 = ResolvedSubmissionParties(
        requester=parties1.requester,
        supplier=supplier2,
    )

    resolver = SubmissionRelationResolver(
        relation_service=service,
    )

    relation1 = resolver.resolve(
        parties1
    )

    relation2 = resolver.resolve(
        parties2
    )

    assert relation1 is not relation2

    assert (
        relation1.requester
        is relation2.requester
    )

    assert (
        relation1.supplier
        is not relation2.supplier
    )

    assert len(
        service.list_relations()
    ) == 2


def test_relation_resolver_rejects_invalid_parties():
    service = SupplyChainRelationService()

    resolver = SubmissionRelationResolver(
        relation_service=service,
    )

    with pytest.raises(
        TypeError,
        match=(
            "parties must be "
            "ResolvedSubmissionParties"
        ),
    ):
        resolver.resolve(None)
