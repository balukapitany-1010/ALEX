import pytest
from datetime import datetime

from alex.esg.domain import submission
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.domain.submission import Submission


def test_submission_belongs_to_relation():
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

    submission = Submission(
        relation=relation,
        period="2026-Q2",
        submitter=supplier,
    )

    assert submission.relation is relation
    assert submission.period == "2026-Q2"


def test_submission_rejects_invalid_relation():
    with pytest.raises(TypeError):
        Submission(
            relation="hibás kapcsolat",
            period="2026-Q2",
        )


def test_submission_rejects_empty_period():
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

    with pytest.raises(ValueError):
        Submission(
            relation=relation,
            period="",
            submitter=supplier,
        )

def test_submission_generates_submission_id():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    submission = Submission(
        relation = relation,
        period = "2026-Q2",
        submitter=supplier,
    )
    assert submission.submission_id is not None
    assert isinstance(submission.submission_id, str)
    assert len(submission.submission_id) > 0


def test_submission_have_uniqe_ids():
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
    submission1 = Submission(
        relation=relation,
        period="2026-Q1",
        submitter = supplier,
    )
    submission2 = Submission(
        relation=relation,
        period="2026-Q2",
        submitter = supplier,
    )

    assert submission1.submission_id != submission2.submission_id

def test_submission_has_submitter():
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

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
    )

    assert submission.submitter is supplier


def test_submission_rejects_invalid_submitter():
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

    with pytest.raises(TypeError):
        Submission(
            relation=relation,
            submitter="Nem Company objektum",
            period="2026-Q2",
        )

def test_submission_submitted_at_can_be_none():
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
    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
    )
    assert submission.submitted_at is None


def test_submission_accepts_submited_at():
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
    submitted_at = datetime(2026, 8, 4, 8, 46, 12)
    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        submitted_at=submitted_at,
    )
    assert submission.submitted_at == submitted_at


def test_submission_rejects_invalid_submitted_at():
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

    with pytest.raises(TypeError):
        Submission(
            relation=relation,
            submitter=supplier,
            period="2026-Q2",
            submitted_at="2026-08-04",
        )

def test_submission_has_created_at():
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

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
    )

    assert submission.created_at is not None
    assert isinstance(submission.created_at, datetime)

def test_submission_has_updated_at():
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

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
    )

    assert submission.updated_at is not None
    assert isinstance(submission.updated_at, datetime)
    assert submission.updated_at == submission.created_at