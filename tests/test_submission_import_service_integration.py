from pathlib import Path

import pytest

from alex.esg.domain.company import Company
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.services.json_import_service import (
    JsonImportService,
)
from alex.esg.services.submission_import_service import (
    SubmissionImportService,
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


def _create_submission(
    questionnaire,
) -> Submission:
    requester = Company(
        name="Teszt Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )

    supplier = Supplier(
        name="Teszt Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    return Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q1",
    )


def test_real_response_adds_all_answers_to_submission():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    batch_data = json_service.load_file(
        SUBMISSION_FILE
    )

    definition_mapper = (
        QuestionnaireDefinitionMapper()
    )

    questionnaire, definitions = (
        definition_mapper.map(
            definition_data,
            questionnaire_code="SZTFH-ESG",
        )
    )

    submission = _create_submission(
        questionnaire
    )

    response_data = (
        batch_data["submissions"][0]["response"]
    )

    service = SubmissionImportService()

    answers = service.import_answers(
        response_data,
        submission=submission,
        question_definitions=definitions,
    )

    assert len(definitions) == 221
    assert len(response_data["questions"]) == 221

    assert len(answers) == 221
    assert len(submission.answers) == 221

    assert all(
        answer.submission is submission
        for answer in answers
    )

    assert all(
        answer in submission.answers
        for answer in answers
    )

    answer_keys = {
        answer.answer_key
        for answer in answers
    }

    assert len(answer_keys) == 221

    answer_value_count = sum(
        len(answer.values)
        for answer in answers
    )

    answered_count = sum(
        1
        for answer in answers
        if answer.is_answered
    )

    print()
    print("=" * 72)
    print("VALÓS SUBMISSION DOMAIN FELÉPÍTÉS")
    print("=" * 72)

    print(
        f"QuestionDefinition: "
        f"{len(definitions)}"
    )

    print(
        f"Response question: "
        f"{len(response_data['questions'])}"
    )

    print(
        f"Answer létrehozva: "
        f"{len(answers)}"
    )

    print(
        f"Submission.answers: "
        f"{len(submission.answers)}"
    )

    print(
        f"AnswerValue: "
        f"{answer_value_count}"
    )

    print(
        f"Megválaszolt Answer: "
        f"{answered_count}"
    )

    print(
        f"Nem megválaszolt Answer: "
        f"{len(answers) - answered_count}"
    )

    print("=" * 72)

def test_real_import_rejects_version_mismatch():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    batch_data = json_service.load_file(
        SUBMISSION_FILE
    )

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, _ = mapper.map(
        definition_data,
        questionnaire_code="SZTFH-ESG",
    )

    submission = _create_submission(
        questionnaire
    )

    service = SubmissionImportService()

    with pytest.raises(
        ValueError,
        match="does not match JSON spec_version",
    ):
        service.validate_spec_version(
            batch_data,
            submission=submission,
        )