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
from alex.esg.mappers.submission_answer_mapper import (
    SubmissionAnswerMapper,
)


def test_mapper_maps_single_field():
    data = {
        "id": "04F1C68B",
        "question_id": "E2",
        "fields": [
            {
                "type": "single",
                "values": [
                    {
                        "optionId": "04F1C68B_1",
                        "selected": True,
                    },
                    {
                        "optionId": "04F1C68B_2",
                        "selected": False,
                    },
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 2

    assert values[0].field_type == "single"
    assert values[0].option_id == "04F1C68B_1"
    assert values[0].selected is True

    assert values[1].selected is False


def test_mapper_maps_text_field():
    data = {
        "id": "04F1C68B_DETAIL",
        "question_id": "E2_detail",
        "fields": [
            {
                "type": "text",
                "values": [
                    {
                        "value": "Teszt szöveg"
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1
    assert values[0].field_type == "text"
    assert values[0].text_value == "Teszt szöveg"
    assert values[0].is_answered is True


def test_mapper_maps_number_field():
    data = {
        "id": "0364FD79",
        "question_id": "E5",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0364FD79_1",
                        "value": 1250.5,
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1

    assert (
        values[0].option_id
        == "0364FD79_1"
    )

    assert values[0].number_value == 1250.5


def test_mapper_maps_mixed_question_fields():
    data = {
        "id": "0319A12E",
        "question_id": "E6",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_1",
                        "value": 25.5,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_2",
                        "value": 10.0,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_3",
                        "value": 24.1,
                    }
                ],
            },
            {
                "type": "multi",
                "values": [
                    {
                        "optionId": "0319A12E_4",
                        "selected": False,
                    }
                ],
            },
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 4

    assert values[0].number_value == 25.5
    assert values[1].number_value == 10.0
    assert values[2].number_value == 24.1

    assert values[3].field_type == "multi"
    assert values[3].selected is False

def test_mapper_allows_number_without_option_id():
    data = {
        "id": "TEST",
        "question_id": "TEST",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "value": None
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1
    assert values[0].option_id is None
    assert values[0].number_value is None
    assert values[0].is_answered is False

def test_mapper_rejects_unknown_field_type():
    data = {
        "id": "TEST",
        "question_id": "TEST",
        "fields": [
            {
                "type": "invalid",
                "values": [],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    with pytest.raises(
        ValueError,
        match="unsupported field type",
    ):
        mapper.map_values(data)
def _create_submission(
    questionnaire: Questionnaire,
) -> Submission:
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

    return Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q1",
    )

def test_mapper_maps_json_question_to_answer():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    question = Question(
        question_id="04F1C68B_DETAIL",
        question_code="E2_detail",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Igen válasz esetén fejtse ki.",
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

    question_data = {
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

    mapper = SubmissionAnswerMapper()

    answer = mapper.map_answer(
        question_data,
        submission=submission,
        question_definitions=(
            definition,
        ),
    )

    assert answer.submission is submission

    assert (
        answer.question_definition
        is definition
    )

    assert len(answer.values) == 1

    assert (
        answer.values[0].text_value
        == "Teszt válasz"
    )

    assert answer.is_answered is True


def test_mapper_maps_mixed_json_question_to_answer():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    question = Question(
        question_id="0319A12E",
        question_code="E6",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title=(
            "A felhasznált villamos energia "
            "hány százaléka származott "
            "megújuló forrásból?"
        ),
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Éghajlatváltozás",
        subtopic="Energiagazdálkodás",
        question_type=QuestionType.MIXED,
    )

    question_data = {
        "id": "0319A12E",
        "question_id": "E6",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_1",
                        "value": 25.5,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_2",
                        "value": 10.0,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_3",
                        "value": 24.1,
                    }
                ],
            },
            {
                "type": "multi",
                "values": [
                    {
                        "optionId": "0319A12E_4",
                        "selected": False,
                    }
                ],
            },
        ],
    }

    mapper = SubmissionAnswerMapper()

    answer = mapper.map_answer(
        question_data,
        submission=submission,
        question_definitions=(
            definition,
        ),
    )

    assert len(answer.values) == 4

    assert answer.values[0].number_value == 25.5
    assert answer.values[1].number_value == 10.0
    assert answer.values[2].number_value == 24.1

    assert answer.values[3].selected is False

    assert answer.is_answered is True

def test_mapper_rejects_unknown_question_id():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    question_data = {
        "id": "DOES_NOT_EXIST",
        "question_id": "UNKNOWN",
        "fields": [],
    }

    mapper = SubmissionAnswerMapper()

    with pytest.raises(
        ValueError,
        match="question definition not found",
    ):
        mapper.map_answer(
            question_data,
            submission=submission,
            question_definitions=(),
        )

def test_mapper_uses_technical_id_as_primary_key():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    question = Question(
        question_id="04DFCA6B_DETAIL1",
        question_code="G9_detail",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.G,
        subject="Governance",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Teszt",
        question_type=QuestionType.TEXT,
    )

    question_data = {
        "id": "04DFCA6B_DETAIL1",
        "question_id": "G9_detail1",
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

    mapper = SubmissionAnswerMapper()

    answer = mapper.map_answer(
        question_data,
        submission=submission,
        question_definitions=(
            definition,
        ),
    )

    assert (
        answer.question_definition
        is definition
    )

def test_mapper_maps_all_response_questions():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    question1 = Question(
        question_id="04F1C68B_DETAIL",
        question_code="E2_detail",
    )

    definition1 = QuestionDefinition(
        question=question1,
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

    question2 = Question(
        question_id="0364FD79",
        question_code="E5",
    )

    definition2 = QuestionDefinition(
        question=question2,
        questionnaire=questionnaire,
        title="Teljes energiafogyasztás",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Éghajlatváltozás",
        question_type=QuestionType.MIXED,
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
            },
            {
                "id": "0364FD79",
                "question_id": "E5",
                "fields": [
                    {
                        "type": "number",
                        "values": [
                            {
                                "optionId": "0364FD79_1",
                                "value": 1250.5,
                            }
                        ],
                    }
                ],
            },
        ]
    }

    mapper = SubmissionAnswerMapper()

    answers = mapper.map_answers(
        response_data,
        submission=submission,
        question_definitions=(
            definition1,
            definition2,
        ),
    )

    assert len(answers) == 2

    assert (
        answers[0].question_definition
        is definition1
    )

    assert (
        answers[0].values[0].text_value
        == "Teszt válasz"
    )

    assert (
        answers[1].question_definition
        is definition2
    )

    assert (
        answers[1].values[0].number_value
        == 1250.5
    )

def test_mapper_rejects_duplicate_response_question_ids():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    submission = _create_submission(
        questionnaire
    )

    response_data = {
        "questions": [
            {
                "id": "TEST_ID",
                "question_id": "TEST",
                "fields": [],
            },
            {
                "id": "TEST_ID",
                "question_id": "TEST",
                "fields": [],
            },
        ]
    }

    mapper = SubmissionAnswerMapper()

    with pytest.raises(
        ValueError,
        match="duplicate response question id",
    ):
        mapper.map_answers(
            response_data,
            submission=submission,
            question_definitions=(),
        )