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
        organization = "SZTFH",
        organization_sizes = ["Large", "Medium", "company_subject_to_the_ESG_ACT",],
        geographical_relevance = ["HU/EGT/Switzerland", "OECD", "Other",],
        topic = "teszt topic",
        subtopic = None,
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
            organization="SZTFH",
            organization_sizes=["Large" ],
            geographical_relevance=["HU/EGT/Switzerland" ],
            topic="teszt topic",
            subtopic=None,
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
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="teszt topic",
            subtopic=None,
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
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="teszt topic",
            subtopic=None,
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
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="teszt topic",
        subtopic=None,
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
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="teszt topic",
            subtopic=None,
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
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="teszt topic",
        subtopic=None,
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
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="teszt topic",
            subtopic=None,
        )

def test_question_definition_has_organization_metadata():
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
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=[
            "Large",
            "Medium",
            "company_subject_to_the_ESG_Act",
        ],
        geographical_relevance=[
            "HU/EGT/Switzerland",
            "OECD",
            "Other",
        ],
        topic="teszt topic",
        subtopic=None,
    )

    assert definition.organization == "SZTFH"

    assert definition.organization_sizes == [
        "Large",
        "Medium",
        "company_subject_to_the_ESG_Act",
    ]

    assert definition.geographical_relevance == [
        "HU/EGT/Switzerland",
        "OECD",
        "Other",
    ]

def test_question_definition_rejects_invalid_organization_sizes():
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
            category=QuestionCategory.E,
            subject="Teszt",
            organization="SZTFH",
            organization_sizes="Large",
            geographical_relevance=["OECD"],
            topic="teszt topic",
            subtopic=None,
        )
def test_question_definition_rejects_invalid_geographical_relevance():
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
            category=QuestionCategory.E,
            subject="Teszt",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance="OECD",
            topic="teszt topic",
            subtopic=None,
        )
def test_question_definition_has_topic_subtopic():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version = "2.1",
        locale = "hu",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt kérdés",
        category = QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization = "SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic = "Energia",
        subtopic = "Megújuló energia",
    )
    assert definition.topic == "Energia"
    assert definition.subtopic == "Megújuló energia"

def test_question_definition_subtopic_van_be_none():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version = "2.1",
        locale = "hu",

    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt kérdés",
        category = QuestionCategory.E,
        subject = "Környezeti Fenntarthatóság",
        organization = "SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic = "Energia",

    )
    assert definition.subtopic is None