import pytest

from alex.esg.domain import submission
from alex.esg.domain.option import Option
from alex.esg.domain.answer import Answer
from alex.esg.domain.company import Company
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation

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

    assert answer.selected_options == [option]

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