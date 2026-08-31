from pathlib import Path

from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.services.json_import_service import (
    JsonImportService,
)
from alex.esg.services.questionnaire_compatibility_service import (
    QuestionnaireCompatibilityService,
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


def test_real_2_0_definition_against_2_1_submission():
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

    service = QuestionnaireCompatibilityService()

    result = service.analyze(
        submission_data,
        questionnaire=questionnaire,
        question_definitions=definitions,
    )

    assert result.definition_version == "2.0"
    assert result.submission_version == "2.1"

    assert result.version_matches is False

    assert result.definition_count == 221

    assert result.response_question_count > 0

    assert (
        result.matched_question_count
        <= result.response_question_count
    )


def test_real_2_0_to_2_1_compatibility_report():
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

    service = QuestionnaireCompatibilityService()

    result = service.analyze(
        submission_data,
        questionnaire=questionnaire,
        question_definitions=definitions,
    )

    print()
    print("=" * 72)
    print("2.0 DEFINÍCIÓ / 2.1 VÁLASZ KOMPATIBILITÁS")
    print("=" * 72)

    print(
        f"Definíció verzió: "
        f"{result.definition_version}"
    )

    print(
        f"Válasz verzió: "
        f"{result.submission_version}"
    )

    print(
        f"Verzió egyezik: "
        f"{result.version_matches}"
    )

    print()

    print(
        f"Definíciók száma: "
        f"{result.definition_count}"
    )

    print(
        f"Response kérdések száma: "
        f"{result.response_question_count}"
    )

    print(
        f"Technical ID alapján illeszkedik: "
        f"{result.matched_question_count}"
    )

    unmatched_count = (
        result.response_question_count
        - result.matched_question_count
    )

    print(
        f"Nem illeszkedő technical ID: "
        f"{unmatched_count}"
    )

    print()

    print(
        f"QUESTION_DEFINITION_NOT_FOUND: "
        f"{result.unknown_question_count}"
    )

    print(
        f"QUESTION_CODE_MISMATCH: "
        f"{result.question_code_mismatch_count}"
    )

    print(
        f"UNKNOWN_OPTION_ID: "
        f"{result.unknown_option_id_count}"
    )

    print()

    print(
        f"Összes ERROR: "
        f"{len(result.errors)}"
    )

    print(
        f"Összes WARNING: "
        f"{len(result.warnings)}"
    )

    print(
        f"Strukturálisan kompatibilis: "
        f"{result.is_structurally_compatible}"
    )

    print()

    if result.issues:
        print("RÉSZLETES ELTÉRÉSEK")
        print("-" * 72)

        for issue in result.issues:
            print(
                f"[{issue.severity.value.upper()}] "
                f"{issue.code}: "
                f"{issue.message}"
            )

    print("=" * 72)

    assert (
        result.definition_count
        == len(definitions)
    )

    assert (
        result.response_question_count
        >= result.matched_question_count
    )
    assert result.definition_count == 221
    assert result.response_question_count == 221
    assert result.matched_question_count == 221

    assert result.unknown_question_count == 0

    assert (
            result.question_code_mismatch_count
            == 1
    )

    assert result.unknown_option_id_count == 0

    assert result.errors == ()

    assert len(result.warnings) == 1

    assert (
            result.warnings[0].code
            == "QUESTION_CODE_MISMATCH"
    )

    assert (
            result.is_structurally_compatible
            is True
    )

