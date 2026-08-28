import pytest
from datetime import datetime
from alex.esg.domain.answer import Answer
from alex.esg.domain.company import Company
from alex.esg.domain.option import Option
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.domain.answer_value import AnswerValue

def test_answer_connects_submission_and_question():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,

    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.submission is submission
    assert answer.question_definition is definition

def test_answer_rejects_invalid_submission():
    with pytest.raises(TypeError):
        Answer(
            submission = "hibás submission",
            question_definition = None,
        )

def test_answer_rejects_invalid_question_definition():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester = requester,
        supplier = supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code = "SZTFH",
        spec_version = "2.1",
        locale = "hu",
    )
    submission = Submission(
        relation = relation,
        submitter = supplier,
        questionnaire = questionnaire,
        period = "2026-Q2",
    )
    with pytest.raises(TypeError):
        Answer(
            submission = submission,
            question_definition = "E1",
        )

def test_answer_can_have_selected_options():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options=[option],
    )

    assert answer.selected_options == (option,)

def test_answer_rejects_invalid_selected_options():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    with pytest.raises(TypeError):
        Answer(
            submission=submission,
            question_definition=definition,
            selected_options=["Igen"],
        )

def test_answer_rejects_option_not_belonging_to_question():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    valid_option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[valid_option],
    )

    foreign_option = Option(
        option_id="99999999_1",
        label="Idegen opció",
    )

    with pytest.raises(ValueError):
        Answer(
            submission=submission,
            question_definition=definition,
            selected_options=[foreign_option],
        )

def test_radio_answer_rejects_multiple_selected_options():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
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
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[yes_option, no_option],
    )

    with pytest.raises(ValueError):
        Answer(
            submission=submission,
            question_definition=definition,
            selected_options=[yes_option, no_option],
        )

def test_answer_can_have_text_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="A vállalkozás 2026-ban új intézkedést vezetett be.",
    )

    assert answer.text_value == (
        "A vállalkozás 2026-ban új intézkedést vezetett be."
    )
def test_answer_text_value_defaults_to_none():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.text_value is None

def test_radio_answer_rejects_text_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
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
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[yes_option, no_option],
    )

    with pytest.raises(ValueError):
        Answer(
            submission=submission,
            question_definition=definition,
            text_value="Igen",
        )

def test_answer_rejects_invalid_text_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    with pytest.raises(TypeError):
        Answer(
            submission=submission,
            question_definition=definition,
            text_value=123,
        )

def test_answer_can_have_number_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value = 125.5,
    )
    assert answer.number_value == 125.5


def test_answer_number_value_defaults_to_none():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    assert answer.number_value is None

def test_answer_rejects_invalid_number_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )

    with pytest.raises(TypeError):
        Answer(
            submission=submission,
            question_definition=definition,
            number_value="125.5",
        )

def test_answer_rejects_boolean_as_number_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )
    with pytest.raises(TypeError):
        Answer(
            submission=submission,
            question_definition=definition,
            number_value=True,
        )

def test_radio_answer_rejects_number_value():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
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
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[yes_option, no_option],
    )

    with pytest.raises(ValueError):
        Answer(
            submission=submission,
            question_definition=definition,
            number_value=123,
        )


def test_mixed_answer_can_have_optoin_and_text_value():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E20",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt kérdés",
        category=QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
        options=[option],
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options = [option],
        text_value = "Kiegészítő információ",
    )
    assert answer.selected_options == (option,)
    assert answer.text_value == "Kiegészítő információ"


def test_answer_can_have_option_text_and_number_value():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E20",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt mixed kérdés",
        category=QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
        options=[option],
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options=[option],
        text_value = "Megjegyzés",
        number_value = 125.5,
    )
    assert answer.selected_options == (option,)
    assert answer.text_value == "Megjegyzés"
    assert answer.number_value == 125.5

def test_empty_radio_answer_is_not_answered():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-11",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title = "Teszt kérdés",
        category=QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[option],
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    assert answer.selected_options == ()
    assert answer.is_answered is False

def test_radio_answer_with_selected_option_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.RADIO,
        options=[option],
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options = [option],
    )
    assert answer.is_answered is True

def test_checkbox_answer_with_one_sselected_option_is_answerd():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    option1 = Option(
        option_id="3737695_1",
        label="Elsdő",
    )
    option2 = Option(
        option_id="3737695_2",
        label = "Második",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.CHECKBOX,
        options=[option1, option2],
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options=[option1],
    )
    assert answer.is_answered is True

def test_empty_text_answer_is_not_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    assert  answer.text_value is None
    assert answer.is_answered is False

def test_text_answer_with_value_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )
    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value = "Kitöltött válasz",
    )
    assert answer.is_answered is True

def test_number_answer_with_zero_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt számos kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value=0,
    )

    assert answer.is_answered is True

def test_empty_mixed_answer_is_not_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt mixed kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.is_answered is False
def test_mixed_answer_with_selected_option_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt mixed kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options=[option],
    )

    assert answer.is_answered is True

def test_mixed_answer_with_text_value_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E20",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt mixed kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Kiegészítő információ",
    )

    assert answer.selected_options == ()
    assert answer.text_value == "Kiegészítő információ"
    assert answer.number_value is None
    assert answer.is_answered is True

def test_mixed_answer_with_number_value_is_answered():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E20",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt mixed kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value=125.5,
    )

    assert answer.selected_options == ()
    assert answer.text_value is None
    assert answer.number_value == 125.5
    assert answer.is_answered is True

def test_answer_rejects_question_definition_from_different_questionnaire():
    requester = Company(
        name = "Megrendelő Kft.",
        tax_number = "11111111-1-1",
    )
    supplier = Supplier(
        name = "Beszállító Kft.",
        tax_number = "22222222-2-2",
    )
    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )
    questionnaire_21 = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    questionnaire_22 = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.2",
        locale="hu",
    )
    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire_21,
        period="2026-Q2",
    )
    question = Question(
        question_id="3737695",
        question_code="E1",
    )
    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire_22,
        title = "Teszt kérdés",
        category=QuestionCategory.E,
        subject = "Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )
    with pytest.raises(ValueError):
        Answer(
            submission=submission,
            question_definition=definition,
        )

def test_answer_accepts_same_logical_questionnaire():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-1",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-2",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    submission_questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    definition_questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=submission_questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=definition_questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.question_definition is definition


def test_answer_generates_answer_id():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
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

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.answer_id is not None
    assert isinstance(answer.answer_id, str)
    assert len(answer.answer_id) > 0

def test_answers_have_unique_ids():
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    question = Question(
        question_id="3737695",
        question_code="E1",
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

    answer1 = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer1.answer_id != answer2.answer_id

def test_answer_key_contains_submission_and_question_id():
    def create_questionnaire() -> Questionnaire:
        return Questionnaire(
            questionnaire_code="SZTFH",
            spec_version="2.1",
            locale="hu",
        )

    def create_submission(
            questionnaire: Questionnaire | None = None,
    ) -> Submission:
        requester = Company(
            name="Megrendelő Kft.",
            tax_number="11111111-1-11",
        )

        supplier = Supplier(
            name="Beszállító Kft.",
            tax_number="22222222-2-22",
        )

        relation = SupplyChainRelation(
            requester=requester,
            supplier=supplier,
        )

        if questionnaire is None:
            questionnaire = create_questionnaire()

        return Submission(
            relation=relation,
            submitter=supplier,
            questionnaire=questionnaire,
            period="2026-Q2",
        )

    def create_question_definition(
            questionnaire: Questionnaire,
            question_type: QuestionType = QuestionType.TEXT,
            options: list[Option] | None = None,
            question_id: str = "3737695",
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
            subject="Környezeti Fenntarthatóság",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="Energia",
            question_type=question_type,
            options=options,
        )
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    expected = (
        f"{submission.submission_id}:"
        f"{definition.question.question_id}"
    )

    assert answer.answer_key == expected


def test_answers_for_same_submission_and_question_have_same_answer_key():
    def create_questionnaire() -> Questionnaire:
        return Questionnaire(
            questionnaire_code="SZTFH",
            spec_version="2.1",
            locale="hu",
        )

    def create_submission(
            questionnaire: Questionnaire | None = None,
    ) -> Submission:
        requester = Company(
            name="Megrendelő Kft.",
            tax_number="11111111-1-11",
        )

        supplier = Supplier(
            name="Beszállító Kft.",
            tax_number="22222222-2-22",
        )

        relation = SupplyChainRelation(
            requester=requester,
            supplier=supplier,
        )

        if questionnaire is None:
            questionnaire = create_questionnaire()

        return Submission(
            relation=relation,
            submitter=supplier,
            questionnaire=questionnaire,
            period="2026-Q2",
        )

    def create_question_definition(
            questionnaire: Questionnaire,
            question_type: QuestionType = QuestionType.TEXT,
            options: list[Option] | None = None,
            question_id: str = "3737695",
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
            subject="Környezeti Fenntarthatóság",
            organization="SZTFH",
            organization_sizes=["Large"],
            geographical_relevance=["HU/EGT/Switzerland"],
            topic="Energia",
            question_type=question_type,
            options=options,
        )
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer1.answer_id != answer2.answer_id
    assert answer1.answer_key == answer2.answer_key
def create_questionnaire() -> Questionnaire:
    return Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )


def create_submission(
    questionnaire: Questionnaire | None = None,
) -> Submission:
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    if questionnaire is None:
        questionnaire = create_questionnaire()

    return Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )


def create_question_definition(
    questionnaire: Questionnaire,
    question_type: QuestionType = QuestionType.TEXT,
    options: list[Option] | None = None,
    question_id: str = "3737695",
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
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=question_type,
        options=options,
    )

def test_answer_has_created_at():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.created_at is not None
    assert isinstance(answer.created_at, datetime)


def test_answer_has_updated_at():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert answer.updated_at is not None
    assert isinstance(answer.updated_at, datetime)
    assert answer.updated_at == answer.created_at

def test_answer_text_value_can_be_updated():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Eredeti válasz",
    )

    previous_updated_at = answer.updated_at

    answer.set_text_value("Módosított válasz")

    assert answer.text_value == "Módosított válasz"
    assert answer.updated_at >= previous_updated_at


def test_answer_text_value_can_be_cleared():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Eredeti válasz",
    )

    assert answer.is_answered is True

    answer.set_text_value(None)

    assert answer.text_value is None
    assert answer.is_answered is False


def test_setting_same_text_value_does_not_update_updated_at():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Eredeti válasz",
    )

    previous_updated_at = answer.updated_at

    answer.set_text_value("Eredeti válasz")

    assert answer.updated_at == previous_updated_at


def test_set_text_value_rejects_invalid_type():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(TypeError):
        answer.set_text_value(123)


def test_set_text_value_rejects_text_for_radio_question():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.RADIO,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(ValueError):
        answer.set_text_value("Nem megengedett")

# -------------------------------------------------------------------------
# set_number_value
# -------------------------------------------------------------------------


def test_answer_number_value_can_be_updated():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value=100,
    )

    previous_updated_at = answer.updated_at

    answer.set_number_value(125.5)

    assert answer.number_value == 125.5
    assert answer.updated_at >= previous_updated_at


def test_answer_number_value_can_be_cleared():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value=125.5,
    )

    assert answer.is_answered is True

    answer.set_number_value(None)

    assert answer.number_value is None
    assert answer.is_answered is False


def test_setting_same_number_value_does_not_update_updated_at():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        number_value=125.5,
    )

    previous_updated_at = answer.updated_at

    answer.set_number_value(125.5)

    assert answer.number_value == 125.5
    assert answer.updated_at == previous_updated_at


def test_set_number_value_accepts_zero():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.set_number_value(0)

    assert answer.number_value == 0
    assert answer.is_answered is True


def test_set_number_value_rejects_invalid_type():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(TypeError):
        answer.set_number_value("125.5")


def test_set_number_value_rejects_boolean():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(TypeError):
        answer.set_number_value(True)


def test_set_number_value_rejects_number_for_text_question():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(ValueError):
        answer.set_number_value(42)


def test_mixed_answer_number_value_can_be_updated():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.set_number_value(42)

    assert answer.number_value == 42
    assert answer.is_answered is True




def test_checkbox_option_can_be_selected():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Első",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.select_option(option)

    assert answer.selected_options == (option,)
    assert answer.is_answered is True


def test_checkbox_can_have_multiple_selected_options():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option1 = Option(
        option_id="3737695_1",
        label="Első",
    )

    option2 = Option(
        option_id="3737695_2",
        label="Második",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option1, option2],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.select_option(option1)
    answer.select_option(option2)

    assert answer.selected_options == (
        option1,
        option2,
    )


def test_selecting_same_checkbox_option_twice_does_not_duplicate_it():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Első",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.select_option(option)
    previous_updated_at = answer.updated_at

    answer.select_option(option)

    assert answer.selected_options == (option,)
    assert answer.updated_at == previous_updated_at


def test_radio_selecting_new_option_replaces_previous_option():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    yes_option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    no_option = Option(
        option_id="3737695_2",
        label="Nem",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.RADIO,
        options=[yes_option, no_option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    answer.select_option(yes_option)
    answer.select_option(no_option)

    assert answer.selected_options == (no_option,)


def test_option_can_be_unselected():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Első",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        selected_options=[option],
    )

    assert answer.is_answered is True

    answer.unselect_option(option)

    assert answer.selected_options == ()
    assert answer.is_answered is False


def test_unselecting_not_selected_option_does_not_update_answer():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Első",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    previous_updated_at = answer.updated_at

    answer.unselect_option(option)

    assert answer.selected_options == ()
    assert answer.updated_at == previous_updated_at


def test_select_option_rejects_foreign_option():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    allowed_option = Option(
        option_id="3737695_1",
        label="Engedélyezett",
    )

    foreign_option = Option(
        option_id="9999999_1",
        label="Idegen",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[allowed_option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(ValueError):
        answer.select_option(foreign_option)


def test_select_option_rejects_option_for_text_question():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(ValueError):
        answer.select_option(option)


def test_select_option_rejects_invalid_type():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(TypeError):
        answer.select_option("Igen")




def test_text_value_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(AttributeError):
        answer.text_value = "Közvetlen módosítás"


def test_number_value_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.NUMBER,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(AttributeError):
        answer.number_value = 42


def test_selected_options_cannot_be_modified_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.CHECKBOX,
        options=[option],
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    assert isinstance(answer.selected_options, tuple)

    with pytest.raises(AttributeError):
        answer.selected_options.append(option)

# -------------------------------------------------------------------------
# Answer relationship encapsulation
# -------------------------------------------------------------------------


def test_answer_submission_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    other_submission = create_submission(questionnaire)

    with pytest.raises(AttributeError):
        answer.submission = other_submission


def test_answer_question_definition_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    other_definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
        question_id="3737696",
        question_code="E2",
    )

    with pytest.raises(AttributeError):
        answer.question_definition = other_definition

def test_answer_id_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)
    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    original_answer_id = answer.answer_id
    with pytest.raises(AttributeError):
        answer.answer_id = "new-answer-id"

        assert answer.answer_id != original_answer_id

def test_answer_created_at_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    original_created_at = answer.created_at

    with pytest.raises(AttributeError):
        answer.created_at = datetime.now()
        assert answer.created_at == original_created_at

def test_answer_updated_at_cannot_be_changed_directly():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)
    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.TEXT,
    )
    answer = Answer(
        submission=submission,
        question_definition=definition,
    )
    original_updated_at = answer.updated_at
    with pytest.raises(AttributeError):
        answer.updated_at = datetime.now()
        assert answer.updated_at == original_updated_at

def test_answer_can_have_answer_values():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    value = AnswerValue(
        field_type="text",
        text_value="Teszt érték",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        values=[value],
    )

    assert answer.values == (value,)


def test_answer_rejects_invalid_values():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    with pytest.raises(
        TypeError,
        match="values must be a list or None",
    ):
        Answer(
            submission=submission,
            question_definition=definition,
            values="invalid",
        )

    with pytest.raises(
        TypeError,
        match="values must contain only AnswerValue objects",
    ):
        Answer(
            submission=submission,
            question_definition=definition,
            values=["invalid"],
        )


def test_answer_can_add_value():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    value = AnswerValue(
        field_type="number",
        number_value=42,
    )

    answer.add_value(value)

    assert answer.values == (value,)


def test_answer_rejects_invalid_added_value():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    with pytest.raises(
        TypeError,
        match="value must be an AnswerValue",
    ):
        answer.add_value("invalid")


def test_answer_value_makes_answer_answered():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    value = AnswerValue(
        field_type="text",
        text_value="Van válasz",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        values=[value],
    )

    assert answer.is_answered is True


def test_empty_answer_values_do_not_make_answer_answered():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_question_definition(
        questionnaire=questionnaire,
        question_type=QuestionType.MIXED,
    )

    value = AnswerValue(
        field_type="text",
        text_value=None,
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        values=[value],
    )

    assert answer.is_answered is False