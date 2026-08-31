import pytest
from datetime import datetime
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain import submission
from alex.esg.domain.company import Company
from alex.esg.domain.submission_status import SubmissionStatus
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        period="2026-Q2",
        submitter=supplier,
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    with pytest.raises(ValueError):
        Submission(
            relation=relation,
            period="",
            submitter=supplier,
            questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation = relation,
        period = "2026-Q2",
        submitter=supplier,
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission1 = Submission(
        relation=relation,
        period="2026-Q1",
        submitter = supplier,
        questionnaire=questionnaire,
    )
    submission2 = Submission(
        relation=relation,
        period="2026-Q2",
        submitter = supplier,
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submitted_at = datetime(2026, 8, 4, 8, 46, 12)
    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        submitted_at=submitted_at,
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )

    assert submission.updated_at is not None
    assert isinstance(submission.updated_at, datetime)
    assert submission.updated_at == submission.created_at

def Test_submission_default_status_is_submitted():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    assert submission.status == SubmissionStatus.SUBMITTED

def test_submission_rejects_invalid_status():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    with pytest.raises(TypeError):
        Submission(
            relation=relation,
            submitter=supplier,
            period="2026-Q2",
            status = "submitted",
        )


def test_submission_can_be_archived():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    previus_update_at = submission.updated_at
    submission.archive()
    assert submission.status == SubmissionStatus.ARCHIVED
    assert submission.updated_at >= previus_update_at

def test_arching_already_archived_submission_does_not_update_again():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    submission.archive()
    archived_at = submission.updated_at
    submission.archive()

    assert submission.updated_at == archived_at

def test_submission_status_cannot_be_change_diretly():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    with pytest.raises(AttributeError):
        submission.status = SubmissionStatus.ARCHIVED

def test_archived_submission_van_be_restored():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    submission.archive()
    archived_at = submission.updated_at
    submission.restore()

    assert submission.status == SubmissionStatus.SUBMITTED
    assert submission.updated_at >= archived_at

def test_restoring_submitted_submission_does_not_update_again():
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
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        period="2026-Q2",
        questionnaire=questionnaire,
    )
    previus_update_at = submission.updated_at
    submission.restore()

    assert submission.status == SubmissionStatus.SUBMITTED
    assert submission.updated_at == previus_update_at

def test_submission_has_questionnaire():
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
    questionnaire = Questionnaire(
        questionnaire_code= "SZTFH",
        spec_version= "2.1",
        locale = "hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    assert submission.questionnaire is questionnaire

def test_submission_rejects_invalid_questionnaire():
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
            questionnaire="SZTFH 2.1",
            period="2026-Q2",
        )

def test_submission_can_have_organization_size():
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

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
        organization_size="Large",
    )

    assert submission.organization_size == "Large"


def test_submission_organization_size_can_be_none():
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

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    assert submission.organization_size is None


def test_submission_rejects_invalid_organization_size():
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

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    with pytest.raises(TypeError):
        Submission(
            relation=relation,
            submitter=supplier,
            questionnaire=questionnaire,
            period="2026-Q2",
            organization_size=123,
        )
def test_submission_allows_unknown_submitter():
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

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = Submission(
        relation=relation,
        submitter=None,
        questionnaire=questionnaire,
        period="2026-Q1",
    )

    assert submission.submitter is None
def test_submission_rejects_invalid_submitter():
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

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    with pytest.raises(
        TypeError,
        match="submitter must be a Company or None",
    ):
        Submission(
            relation=relation,
            submitter="invalid",
            questionnaire=questionnaire,
            period="2026-Q1",
        )