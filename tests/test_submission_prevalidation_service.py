from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.submission_prevalidation_service import (
    SubmissionPrevalidationService,
)


def test_prevalidation_rejects_version_mismatch():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.0",
        locale="HU",
    )

    batch_data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [],
    }

    service = SubmissionPrevalidationService()

    result = service.validate(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(),
    )

    assert result.is_valid is False

    assert any(
        issue.code == "QUESTIONNAIRE_VERSION_MISMATCH"
        for issue in result.errors
    )


def test_prevalidation_accepts_matching_empty_batch():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    batch_data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [],
    }

    service = SubmissionPrevalidationService()

    result = service.validate(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(),
    )

    assert result.is_valid is True
    assert result.errors == ()
    assert result.warnings == ()

    assert result.batch_result.spec_version == "2.1"


def test_prevalidation_reports_unknown_question():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    batch_data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
                    "org_size": "Large",
                    "submitted_at": "2026-02-12T11:54:29Z",
                    "cover": {
                        "supplier": {
                            "company": "Beszállító Kft.",
                            "tax_number": "11111111-2-41",
                            "period": "2026-Q1",
                        },
                        "requester": {
                            "company": "ABC Zrt.",
                            "tax_number": "22222222-2-41",
                            "requester_MP_id": "REQ-1",
                        },
                    },
                    "questions": [
                        {
                            "id": "UNKNOWN_ID",
                            "question_id": "E1",
                            "fields": [],
                        }
                    ],
                }
            }
        ],
    }

    service = SubmissionPrevalidationService()

    result = service.validate(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(),
    )

    assert result.is_valid is False

    assert any(
        issue.code == "QUESTION_DEFINITION_NOT_FOUND"
        for issue in result.errors
    )

    assert any(
        issue.message.startswith("submission 0:")
        for issue in result.errors
    )