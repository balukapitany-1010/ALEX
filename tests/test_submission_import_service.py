import pytest
from alex.esg.domain.company import Company
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import (
    QuestionCategory,
)
from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.services.submission_import_service import (
    SubmissionImportService,
)


def _create_submission_and_definition():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    requester = Company(
        name="ABC Zrt.",
        tax_number="12345678-1-11",
        country="HU",
    )

    supplier = Supplier(
        name="Minta Kft.",
        tax_number="11111111-1-11",
        country="HU",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q1",
    )

    question = Question(
        question_id="04F1C68B_DETAIL",
        question_code="E2_detail",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Részletezze a választ.",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Zöld minősítés",
        question_type=QuestionType.COMMENT,
    )

    return submission, definition

def test_submission_import_service_adds_answers():
    submission, definition = (
        _create_submission_and_definition()
    )

    response_data = {
        "questions": [
            {
                "id": "04F1C68B_DETAIL",
                "question_id": "E2_detail",
                "fields": [
                    {
                        "type": "text",
                        "values": [
                            {
                                "value": "Teszt válasz"
                            }
                        ],
                    }
                ],
            }
        ]
    }

    service = SubmissionImportService()

    answers = service.import_answers(
        response_data,
        submission=submission,
        question_definitions=(
            definition,
        ),
    )

    assert len(answers) == 1

    assert len(submission.answers) == 1

    assert (
        submission.answers[0]
        is answers[0]
    )

    assert (
        answers[0].values[0].text_value
        == "Teszt válasz"
    )
def test_submission_import_service_accepts_matching_version():
    submission, _ = (
        _create_submission_and_definition()
    )

    batch_data = {
        "spec_version": "2.1"
    }

    service = SubmissionImportService()

    service.validate_spec_version(
        batch_data,
        submission=submission,
    )

def test_submission_import_service_rejects_wrong_version():
    submission, _ = (
        _create_submission_and_definition()
    )

    batch_data = {
        "spec_version": "2.0"
    }

    service = SubmissionImportService()

    with pytest.raises(ValueError,match="does not match JSON spec_version",):
        service.validate_spec_version(
            batch_data,
            submission=submission,
        )