from pathlib import Path

from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.services.json_import_service import (
    JsonImportService,
)
from alex.esg.services.submission_prevalidation_service import (
    SubmissionPrevalidationService,
)


DATA_DIR = Path(__file__).parent / "data"

DEFINITION_FILE = (
    DATA_DIR
    / "Sztfh_kerdoiv_2_0_HU.json"
)

SUBMISSION_FILE = (
    DATA_DIR
    / "Sztfh_kerdoiv_2_1_valaszminta.json"
)


def test_real_files_report_version_mismatch():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    submission_data = json_service.load_file(
        SUBMISSION_FILE
    )

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, definitions = mapper.map(
        definition_data,
        questionnaire_code="SZTFH-ESG",
    )

    service = SubmissionPrevalidationService()

    result = service.validate(
        submission_data,
        questionnaire=questionnaire,
        question_definitions=definitions,
    )

    assert questionnaire.spec_version == "2.0"

    assert (
        result.batch_result.spec_version
        == "2.1"
    )

    assert result.is_valid is False

    assert any(
        issue.code
        == "QUESTIONNAIRE_VERSION_MISMATCH"
        for issue in result.errors
    )


def test_version_mismatch_stops_definition_validation():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    submission_data = json_service.load_file(
        SUBMISSION_FILE
    )

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, definitions = mapper.map(
        definition_data,
        questionnaire_code="SZTFH-ESG",
    )

    service = SubmissionPrevalidationService()

    result = service.validate(
        submission_data,
        questionnaire=questionnaire,
        question_definitions=definitions,
    )

    issue_codes = {
        issue.code
        for issue in result.issues
    }

    assert (
        "QUESTIONNAIRE_VERSION_MISMATCH"
        in issue_codes
    )

    assert (
        "QUESTION_DEFINITION_NOT_FOUND"
        not in issue_codes
    )

    assert (
        "QUESTION_CODE_MISMATCH"
        not in issue_codes
    )

    assert (
        "UNKNOWN_OPTION_ID"
        not in issue_codes
    )


def test_real_version_mismatch_report():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    submission_data = json_service.load_file(
        SUBMISSION_FILE
    )

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, definitions = mapper.map(
        definition_data,
        questionnaire_code="SZTFH-ESG",
    )

    service = SubmissionPrevalidationService()

    result = service.validate(
        submission_data,
        questionnaire=questionnaire,
        question_definitions=definitions,
    )

    print()
    print("=" * 70)
    print("VALÓS FÁJLOK ELŐVALIDÁCIÓJA")
    print("=" * 70)

    print(
        f"Definíció verzió: "
        f"{questionnaire.spec_version}"
    )

    print(
        f"Válasz verzió: "
        f"{result.batch_result.spec_version}"
    )

    print(
        f"Definíciók száma: "
        f"{len(definitions)}"
    )

    print(
        f"Submissionök száma: "
        f"{result.batch_result.total_count}"
    )

    print(
        f"Batch valid: "
        f"{result.batch_result.valid_count}"
    )

    print(
        f"Batch invalid: "
        f"{result.batch_result.invalid_count}"
    )

    print(
        f"Összes issue: "
        f"{len(result.issues)}"
    )

    print(
        f"Error: "
        f"{len(result.errors)}"
    )

    print(
        f"Warning: "
        f"{len(result.warnings)}"
    )

    print()

    for issue in result.issues:
        print(
            f"[{issue.severity.value.upper()}] "
            f"{issue.code}: "
            f"{issue.message}"
        )

    print("=" * 70)

    assert len(result.errors) == 1

    assert (
        result.errors[0].code
        == "QUESTIONNAIRE_VERSION_MISMATCH"
    )