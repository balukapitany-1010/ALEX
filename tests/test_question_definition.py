import pytest
from unicodedata import category

from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.option import Option

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
        question_type = QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
            question_type=QuestionType.RADIO,
            options=[
                Option(
                    option_id="3737695_1",
                    label="Igen",
                )
            ],
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
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
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
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],

    )
    assert definition.subtopic is None

def test_question_definition_has_question_type():
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
    )

    assert definition.question_type == QuestionType.RADIO


def test_question_definition_rejects_invalid_question_type():
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
            subject="Környezeti Fenntarthatóság",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="Energia",
            question_type="radio",
        )

def test_question_definition_has_requirement():
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        requirement = "Teszt követelmény",
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],
    )
    assert  definition.requirement == "Teszt követelmény"

def test_question_definition_requirement_can_be_none():
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[
            Option(
                option_id="3737695_1",
                label="Igen",
            )
        ],

    )
    assert definition.requirement is None

def test_question_definition_can_have_options():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    yes_option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    no_option = Option(
        option_id="3737695_2",
        label="Nem",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[yes_option, no_option],
    )

    assert definition.options == [yes_option, no_option]

def test_question_definition_options_default_to_empty_list():
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    assert definition.options == []

def test_question_definition_rejects_invalid_option():
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
            subject="Környezeti Fenntarthatóság",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="Energia",
            question_type=QuestionType.RADIO,
            options=["Igen", "Nem"],
        )

def test_question_definition_can_have_options():
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    yes_option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    no_option = Option(
        option_id="3737695_2",
        label="Nem",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt kérdés",
        category=QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization = "SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,

        options=[yes_option, no_option],

    )
    assert definition.options == [yes_option, no_option]


def test_radio_question_requires_option():
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
            title="Teszt kérdés",
            category=QuestionCategory.E,
            subject="Környezeti Fenntarthatóság",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="Energia",
            question_type=QuestionType.RADIO,
        )

def test_text_question_does_not_require_options():
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    assert definition.options == []

def test_question_definition_derives_allowed_value_ids_from_options():
    questionnaire = Questionnaire(
        questionnaire_code="TEST",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="TEST_ID",
        question_code="E1",
    )

    option1 = Option(
        option_id="TEST_ID_1",
        label="Igen",
    )

    option2 = Option(
        option_id="TEST_ID_2",
        label="Nem",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.RADIO,
        options=[
            option1,
            option2,
        ],
    )

    assert (
        definition.allowed_value_ids
        == (
            "TEST_ID_1",
            "TEST_ID_2",
        )
    )

def test_question_definition_accepts_table_value_ids():
    questionnaire = Questionnaire(
        questionnaire_code="TEST",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="TABLE_ID",
        question_code="E17a",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt táblázat",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.TABLE,
        allowed_value_ids=[
            "TABLE_ID_1",
            "TABLE_ID_2",
            "TABLE_ID_3",
        ],
    )

    assert (
        definition.allowed_value_ids
        == (
            "TABLE_ID_1",
            "TABLE_ID_2",
            "TABLE_ID_3",
        )
    )

def test_question_definition_rejects_duplicate_allowed_value_ids():
    questionnaire = Questionnaire(
        questionnaire_code="TEST",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="TABLE_ID",
        question_code="E17a",
    )

    with pytest.raises(
        ValueError,
        match="duplicate allowed value id",
    ):
        QuestionDefinition(
            question=question,
            questionnaire=questionnaire,
            title="Teszt",
            category=QuestionCategory.E,
            subject="Environmental",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU"],
            topic="Teszt",
            question_type=QuestionType.TABLE,
            allowed_value_ids=[
                "TABLE_ID_1",
                "TABLE_ID_1",
            ],
        )