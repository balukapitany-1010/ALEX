import json
from alex.esg.services.questionnaire_service import  QuestionnaireService
from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.submission_batch_importer import SubmissionBatchImporter
from alex.esg.services.submission_definition_validator import SubmissionDefinitionValidator
from alex.esg.services.submission_import_preview_service import SubmissionImportPreviewService


def _create_service():
    return SubmissionImportPreviewService(
        json_service=JsonImportService(),
        definition_mapper=(
            QuestionnaireDefinitionMapper()
        ),
        batch_inspector=(
            SubmissionBatchImporter()
        ),
        definition_validator=(
            SubmissionDefinitionValidator()
        ),
        questionnaire_service=(
            QuestionnaireService()
        ),
    )

def _write_files(
    tmp_path,
    *,
    definition_version="2.1",
    submission_version="2.1",
):
    definition_data = {
        "spec_version": definition_version,
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E1",
                        "title": "Teszt kérdés",
                        "type": "text",
                        "category": "E",
                        "ID": "TEST_ID",
                        "topic": "Teszt",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                        "organization": "SZTFH",
                    }
                ]
            }
        ],
    }

    submission_data = {
        "spec_version": submission_version,
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
                    "org_size": "Large",
                    "submitted_at": (
                        "2026-02-12T11:54:29Z"
                    ),
                    "cover": {
                        "supplier": {
                            "company": (
                                "Beszállító Kft."
                            ),
                            "tax_number": (
                                "11111111-2-41"
                            ),
                            "period": "2026-Q1",
                        },
                        "requester": {
                            "company": (
                                "Kötelezett Zrt."
                            ),
                            "tax_number": (
                                "22222222-2-41"
                            ),
                            "requester_MP_id": (
                                "REQ-1"
                            ),
                        },
                    },
                    "questions": [
                        {
                            "id": "TEST_ID",
                            "question_id": "E1",
                            "fields": [
                                {
                                    "type": "text",
                                    "values": [
                                        {
                                            "value": (
                                                "Teszt válasz"
                                            )
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            }
        ],
    }

    definition_file = (
        tmp_path
        / "definition.json"
    )

    submission_file = (
        tmp_path
        / "submission.json"
    )

    definition_file.write_text(
        json.dumps(
            definition_data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    submission_file.write_text(
        json.dumps(
            submission_data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return (
        definition_file,
        submission_file,
    )


def test_preview_reports_importable_files(tmp_path):
    service = _create_service()

    definition_file, submission_file = (_write_files(tmp_path))

    result = service.preview_files(
        definition_file=definition_file,
        submission_file=submission_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert result.definition_version == "2.1"
    assert result.submission_version == "2.1"

    assert result.version_matches is True

    assert result.definition_count == 1
    assert result.submission_count == 1

    assert (result.response_question_count== 1)

    assert (result.matched_question_count == 1)

    assert result.errors == ()
    assert result.can_import is True


def test_preview_reports_version_mismatch_without_secondary_errors(tmp_path):
    service = _create_service()

    definition_file, submission_file = (_write_files(tmp_path,
            definition_version="2.0",
            submission_version="2.1",
        )
    )

    result = service.preview_files(
        definition_file=definition_file,
        submission_file=submission_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert result.version_matches is False

    assert result.definition_count == 1

    assert (result.response_question_count== 1)

    assert (result.matched_question_count== 1)

    assert result.can_import is False

    assert len(result.errors) == 1

    assert (result.errors[0].code == "QUESTIONNAIRE_VERSION_MISMATCH")

    assert result.warnings == ()