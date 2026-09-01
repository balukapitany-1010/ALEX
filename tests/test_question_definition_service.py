import pytest

from alex.esg.domain.question import  Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import  Questionnaire
from alex.esg.services.question_definition_service import QuestionDefinitionService


def _create_questionnaire(
    *,
    version: str = "2.1",
) -> Questionnaire:
    return Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version=version,
        locale="HU",
    )


def _create_definition(
    questionnaire: Questionnaire,
    *,
    question_id: str = "TEST_ID",
    question_code: str = "E1",
) -> QuestionDefinition:
    question = Question(
        question_id=question_id,
        question_code=question_code,
    )

    return QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=[
            "Large"
        ],
        geographical_relevance=[
            "HU"
        ],
        topic="Teszt",
        question_type=QuestionType.TEXT,
    )


def test_service_adds_definition():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    definition = _create_definition(questionnaire)

    result = service.add_definition(definition)

    assert result is definition

    assert (service.list_definitions() == (definition,))


def test_service_adds_multiple_definitions():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    definition1 = _create_definition(
        questionnaire,
        question_id="ID_1",
        question_code="E1",
    )

    definition2 = _create_definition(
        questionnaire,
        question_id="ID_2",
        question_code="E2",
    )

    result = service.add_definitions(
        (
            definition1,
            definition2,
        )
    )

    assert result == (
        definition1,
        definition2,
    )

    assert len(service.list_definitions()) == 2


def test_service_lists_definitions_for_questionnaire():
    service = QuestionDefinitionService()

    questionnaire_20 = (_create_questionnaire(version="2.0"))

    questionnaire_21 = (_create_questionnaire(version="2.1"))

    definition_20 = _create_definition(questionnaire_20,question_id="ID_1",)

    definition_21 = _create_definition(questionnaire_21,question_id="ID_2",)

    service.add_definition(definition_20)

    service.add_definition(definition_21)

    result = (service.list_for_questionnaire(questionnaire_21))

    assert result == (definition_21,)


def test_service_gets_definition_by_question_id():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    definition = _create_definition(
        questionnaire,
        question_id="04E40FB9",
        question_code="E17a",
    )

    service.add_definition(definition)

    result = service.get_by_question_id(
        questionnaire=questionnaire,
        question_id="04E40FB9",
    )

    assert result is definition


def test_service_returns_none_for_unknown_question():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    result = service.get_by_question_id(
        questionnaire=questionnaire,
        question_id="UNKNOWN",
    )

    assert result is None


def test_service_rejects_duplicate_in_same_questionnaire():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    definition1 = _create_definition(
        questionnaire,
        question_id="TEST_ID",
        question_code="E1",
    )

    definition2 = _create_definition(
        questionnaire,
        question_id="TEST_ID",
        question_code="E1",
    )

    service.add_definition(definition1)

    with pytest.raises(
        ValueError,
        match=("question definition already exists"),
    ):
        service.add_definition(definition2)


def test_same_question_id_is_allowed_in_different_versions():
    service = QuestionDefinitionService()

    questionnaire_20 = (_create_questionnaire(version="2.0"))

    questionnaire_21 = (_create_questionnaire(version="2.1"))

    definition_20 = _create_definition(
        questionnaire_20,
        question_id="SAME_ID",
        question_code="E1",
    )

    definition_21 = _create_definition(
        questionnaire_21,
        question_id="SAME_ID",
        question_code="E1",
    )

    service.add_definition( definition_20)

    service.add_definition(definition_21)

    assert len(service.list_definitions()) == 2

    assert (service.get_by_question_id(
            questionnaire=questionnaire_20,
            question_id="SAME_ID",
        )
        is definition_20
    )

    assert (
        service.get_by_question_id(
            questionnaire=questionnaire_21,
            question_id="SAME_ID",
        )
        is definition_21
    )


def test_service_rejects_invalid_definition():
    service = QuestionDefinitionService()

    with pytest.raises(
        TypeError,
        match=(
            "definition must be a "
            "QuestionDefinition"
        ),
    ):
        service.add_definition("invalid")

def test_register_definitions_adds_new_definitions():
    service = QuestionDefinitionService()

    questionnaire = (
        _create_questionnaire()
    )

    definition1 = _create_definition(
        questionnaire,
        question_id="ID_1",
        question_code="E1",
    )

    definition2 = _create_definition(
        questionnaire,
        question_id="ID_2",
        question_code="E2",
    )

    result = service.register_definitions(
        (
            definition1,
            definition2,
        )
    )

    assert result.definitions == (
        definition1,
        definition2,
    )

    assert result.added == (
        definition1,
        definition2,
    )

    assert result.reused == ()

    assert result.added_count == 2
    assert result.reused_count == 0

    assert len(service.list_definitions()) == 2

def test_register_definitions_reuses_existing_definitions():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    original = _create_definition(
        questionnaire,
        question_id="ID_1",
        question_code="E1",
    )

    service.register_definitions((original,))

    second_instance = _create_definition(
        questionnaire,
        question_id="ID_1",
        question_code="E1",
    )

    result = service.register_definitions((second_instance,))

    assert result.added == ()

    assert result.reused == (original,)

    assert result.definitions == (original,)

    assert (result.definitions[0]is original)

    assert (result.definitions[0]is not second_instance)

    assert len(service.list_definitions()) == 1

def test_register_definitions_rejects_conflicting_question_code():
    service = QuestionDefinitionService()

    questionnaire = (_create_questionnaire())

    original = _create_definition(questionnaire,
        question_id="SAME_ID",
        question_code="E1",
    )

    service.register_definitions((original,))

    conflicting = _create_definition(
        questionnaire,
        question_id="SAME_ID",
        question_code="E99",
    )

    with pytest.raises(
        ValueError,
        match=("conflicting question definition"),
    ):
        service.register_definitions((conflicting,))

    assert (service.list_definitions()== (original,))

def test_register_definitions_allows_same_id_in_new_version():
    service = QuestionDefinitionService()

    questionnaire_20 = (_create_questionnaire(version="2.0"))

    questionnaire_21 = (_create_questionnaire(version="2.1"))

    definition_20 = _create_definition(
        questionnaire_20,
        question_id="SAME_ID",
        question_code="E1",
    )

    definition_21 = _create_definition(
        questionnaire_21,
        question_id="SAME_ID",
        question_code="E1",
    )

    first = service.register_definitions((definition_20,))

    second = service.register_definitions((definition_21,))

    assert first.added_count == 1
    assert second.added_count == 1

    assert len(service.list_definitions()) == 2