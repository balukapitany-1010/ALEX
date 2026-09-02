import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.repositories.in_memory_submission_repository import InMemorySubmissionRepository


def _create_submission() -> Submission:
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

    return Submission(
        relation=relation,
        submitter=None,
        questionnaire=questionnaire,
        period="2026-Q2",
    )


def test_repository_adds_submission():
    repository = (InMemorySubmissionRepository())
    submission = _create_submission()
    result = repository.add(submission)

    assert result is submission
    assert (repository.list_all() == (submission,))


def test_repository_gets_submission_by_id():
    repository = (InMemorySubmissionRepository())
    submission = _create_submission()
    repository.add(submission)
    result = repository.get_by_id(submission.submission_id)

    assert result is submission


def test_repository_returns_none_for_unknown_id():
    repository = (InMemorySubmissionRepository())
    assert (repository.get_by_id("unknown-submission-id") is None)


def test_repository_rejects_duplicate_submission_id():
    repository = (InMemorySubmissionRepository())
    submission = _create_submission()
    repository.add(submission)

    with pytest.raises(
        ValueError,
        match="submission with this id already exists",
    ):
        repository.add(submission)


def test_repository_rejects_invalid_submission():
    repository = (InMemorySubmissionRepository())

    with pytest.raises(
        TypeError,
        match="submission must be a Submission",
    ):
        repository.add( "invalid")


def test_repository_rejects_empty_submission_id():
    repository = (InMemorySubmissionRepository())

    with pytest.raises(
        ValueError,
        match="submission_id cannot be empty",
    ):
        repository.get_by_id("   ")

def test_repository_removes_submission():
    repository = (
        InMemorySubmissionRepository()
    )

    submission = _create_submission()

    repository.add(
        submission
    )

    removed = repository.remove(
        submission.submission_id
    )

    assert removed is submission

    assert (
        repository.list_all()
        == ()
    )

    assert (
        repository.get_by_id(
            submission.submission_id
        )
        is None
    )


def test_repository_rejects_removing_unknown_submission():
    repository = (
        InMemorySubmissionRepository()
    )

    with pytest.raises(
        ValueError,
        match="submission does not exist",
    ):
        repository.remove(
            "unknown-submission-id"
        )