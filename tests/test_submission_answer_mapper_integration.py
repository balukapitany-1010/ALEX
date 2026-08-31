from pathlib import Path

from alex.esg.domain.company import Company
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.mappers.submission_answer_mapper import (
    SubmissionAnswerMapper,
)
from alex.esg.services.json_import_service import (
    JsonImportService,
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


def _create_test_submission(
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


def test_real_response_maps_all_221_answers():
    json_service = JsonImportService()

    definition_data = json_service.load_file(
        DEFINITION_FILE
    )

    submission_data = json_service.load_file(
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

    submission = _create_test_submission(
        questionnaire
    )

    response_data = (
        submission_data["submissions"][0][
            "response"
        ]
    )

    mapper = SubmissionAnswerMapper()

    answers = mapper.map_answers(
        response_data,
        submission=submission,
        question_definitions=definitions,
    )

    assert len(definitions) == 221
    assert len(response_data["questions"]) == 221

    assert len(answers) == 221

    answer_ids = {
        answer.question_definition.question.question_id
        for answer in answers
    }

    assert len(answer_ids) == 221
    assert all(
        answer.submission is submission
        for answer in answers
    )
    assert all(
        answer.question_definition
        in definitions
        for answer in answers
    )
    answer_value_count = sum(
        len(answer.values)
        for answer in answers
    )

    assert answer_value_count > 221

    print()
    print("=" * 72)
    print("VALÓS ANSWER MAPPING")
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
        f"Answer: "
        f"{len(answers)}"
    )

    print(
        f"AnswerValue: "
        f"{answer_value_count}"
    )

    answered_count = sum(
        1
        for answer in answers
        if answer.is_answered
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