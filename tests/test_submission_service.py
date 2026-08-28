import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.services.submission_service import SubmissionService
from alex.esg.domain.answer import Answer
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType


def _create_test_objects():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    return requester, supplier, relation, questionnaire


def test_submission_service_can_create_submission():
    service = SubmissionService()

    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-2-41",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    submission = service.create_submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    assert submission.relation is relation
    assert submission.submitter is supplier
    assert submission.questionnaire is questionnaire
    assert submission.period == "2026-Q2"

def test_submission_service_lists_submissions():
    service = SubmissionService()

    _, supplier, relation, questionnaire = (
        _create_test_objects()
    )

    submission = service.create_submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    assert service.list_submissions() == (
        submission,
    )


def test_submission_service_propagates_domain_validation_error():
    service = SubmissionService()

    _, supplier, relation, questionnaire = (
        _create_test_objects()
    )

    with pytest.raises(ValueError):
        service.create_submission(
            relation=relation,
            submitter=supplier,
            questionnaire=questionnaire,
            period="",
        )

def test_submission_service_can_get_submission_by_id():
    service = SubmissionService()

    _, supplier, relation, questionnaire = (
        _create_test_objects()
    )
    submission = service.create_submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    result = service.get_by_id(
        str(submission.submission_id)
    )
    assert result is submission

def test_submission_can_receive_text_answer():
    service = SubmissionService()

    _, supplier, relation, questionnaire = (
        _create_test_objects()
    )

    submission = service.create_submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="E1",
        question_code="E1",
    )

    question_definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Rendelkezik környezetvédelmi politikával?",
        category=next(iter(QuestionCategory)),
        subject="Környezet",
        organization="Vállalat",
        organization_sizes=[],
        geographical_relevance=[],
        topic="Környezetvédelem",
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=question_definition,
        text_value="Igen, rendelkezik.",
    )

    submission.add_answer(answer)

    assert len(submission.answers) == 1
    assert submission.answers[0] is answer

    assert submission.get_answer(
        "E1"
    ) is answer

    assert submission.has_answer(
        "E1"
    )

    assert submission.is_question_answered(
        "E1"
    )

    assert submission.answered_count == 1