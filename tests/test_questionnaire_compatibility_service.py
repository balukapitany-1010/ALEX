from alex.esg.domain.question import Question
from alex.esg.domain.question_category import (
    QuestionCategory,
)
from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.questionnaire_compatibility_service import (
    QuestionnaireCompatibilityService,
)


def _create_definition():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.0",
        locale="HU",
    )

    question = Question(
        question_id="TEST_ID",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.TEXT,
    )

    return questionnaire, definition


def test_compatibility_service_compares_different_versions():
    questionnaire, definition = (
        _create_definition()
    )

    batch_data = {
        "spec_version": "2.1",
        "submissions": [
            {
                "response": {
                    "questions": [
                        {
                            "id": "TEST_ID",
                            "question_id": "E1",
                            "fields": [
                                {
                                    "type": "text",
                                    "values": [
                                        {
                                            "value": "válasz"
                                        }
                                    ],
                                }
                            ],
                        }
                    ]
                }
            }
        ],
    }

    service = (
        QuestionnaireCompatibilityService()
    )

    result = service.analyze(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.definition_version == "2.0"
    assert result.submission_version == "2.1"

    assert result.version_matches is False

    assert result.definition_count == 1
    assert result.response_question_count == 1
    assert result.matched_question_count == 1

    assert result.errors == ()
    assert result.warnings == ()

    assert (
        result.is_structurally_compatible
        is True
    )

def test_compatibility_service_reports_unknown_question():
    questionnaire, definition = (
        _create_definition()
    )

    batch_data = {
        "spec_version": "2.1",
        "submissions": [
            {
                "response": {
                    "questions": [
                        {
                            "id": "UNKNOWN_ID",
                            "question_id": "E99",
                            "fields": [],
                        }
                    ]
                }
            }
        ],
    }

    service = (
        QuestionnaireCompatibilityService()
    )

    result = service.analyze(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.response_question_count == 1
    assert result.matched_question_count == 0

    assert result.unknown_question_count == 1

    assert (
        result.is_structurally_compatible
        is False
    )
def test_compatibility_service_reports_code_mismatch():
    questionnaire, definition = (
        _create_definition()
    )

    batch_data = {
        "spec_version": "2.1",
        "submissions": [
            {
                "response": {
                    "questions": [
                        {
                            "id": "TEST_ID",
                            "question_id": "E1_CHANGED",
                            "fields": [],
                        }
                    ]
                }
            }
        ],
    }

    service = (
        QuestionnaireCompatibilityService()
    )

    result = service.analyze(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.matched_question_count == 1

    assert (result.question_code_mismatch_count == 1)

    assert result.errors == ()
    assert len(result.warnings) == 1

    assert ( result.is_structurally_compatible is True)