import pytest
from unicodedata import category

from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.question_definition import QuestionDefinition


def test_question_definition_can_be_created():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Használ-e a vállalkozás megújuló energiát?",
        category = QuestionCategory.E,
        subject = "Teszt subjects",
    )

    assert definition.question is question
    assert definition.questionnaire is questionnaire
    assert definition.title == "Használ-e a vállalkozás megújuló energiát?"


def test_question_definition_rejects_invalid_question():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    with pytest.raises(TypeError):
        QuestionDefinition(
            question="E1",
            questionnaire=questionnaire,
            title="Teszt kérdés",
            category=QuestionCategory.E,
            subject="Teszt subjects",
        )


def test_question_definition_rejects_invalid_questionnaire():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    with pytest.raises(TypeError):
        QuestionDefinition(
            question=question,
            questionnaire="SZTFH 2.1",
            title="Teszt kérdés",
            category=QuestionCategory.E,
            subject="Teszt subjects",
        )


def test_question_definition_rejects_empty_title():
    question = Question(
        question_id="3737695",
        question_code="E1",

    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    with pytest.raises(ValueError):
        QuestionDefinition(
            question=question,
            questionnaire=questionnaire,
            title="",
            category=QuestionCategory.E,
            subject="Teszt subjects",
        )

def test_question_definition_has_category():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt Kérdés",
        category = QuestionCategory.E,
        subject="Teszt subjects",
    )

    assert definition.category == QuestionCategory.E

def test_question_definition_rejects_invalid_category():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    with pytest.raises(TypeError):
        QuestionDefinition(
            question=question,
            questionnaire=questionnaire,
            title="Teszt kérdés",
            category = "E",
            subject = "Teszt subjects",
        )

def test_question_definition_has_subject():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt Kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
    )
    assert definition.subject == "Környezeti fenntarthatóság"

def test_question_definition_rejects_empty_subjects():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    with pytest.raises(ValueError):
        QuestionDefinition(
            question=question,
            questionnaire=questionnaire,
            title = "Teszt Kérdés",
            category = QuestionCategory.E,
            subject = "",
        )