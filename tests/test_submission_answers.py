import pytest

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


def create_questionnaire() -> Questionnaire:
    return Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )


def create_submission(
    questionnaire: Questionnaire,
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

    return Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )


def create_definition(
    questionnaire: Questionnaire,
    question_id: str,
    question_code: str,
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
        question_type=QuestionType.TEXT,
    )


def test_submission_can_have_answer():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Teszt válasz",
    )

    submission.add_answer(answer)

    assert submission.answers == (answer,)


def test_submission_can_have_answers_for_different_questions():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition1 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    definition2 = create_definition(
        questionnaire=questionnaire,
        question_id="3737696",
        question_code="E2",
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Első válasz",
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
        text_value="Második válasz",
    )

    submission.add_answer(answer1)
    submission.add_answer(answer2)

    assert submission.answers == (
        answer1,
        answer2,
    )


def test_submission_rejects_second_answer_for_same_question():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition1 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    definition2 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Első válasz",
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
        text_value="Második válasz",
    )

    submission.add_answer(answer1)

    with pytest.raises(ValueError):
        submission.add_answer(answer2)


def test_submission_rejects_answer_from_other_submission():
    questionnaire = create_questionnaire()

    submission1 = create_submission(questionnaire)
    submission2 = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission1,
        question_definition=definition,
        text_value="Teszt válasz",
    )

    with pytest.raises(ValueError):
        submission2.add_answer(answer)


def test_submission_rejects_invalid_answer():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    with pytest.raises(TypeError):
        submission.add_answer("Nem Answer objektum")

def test_submission_can_get_answer_by_question_id():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Teszt válasz",
    )

    submission.add_answer(answer)

    result = submission.get_answer("3737695")

    assert result is answer


def test_submission_get_answer_returns_none_if_question_not_found():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    result = submission.get_answer("9999999")

    assert result is None


def test_submission_get_answer_rejects_empty_question_id():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    with pytest.raises(ValueError):
        submission.get_answer("")

def test_submission_answered_count_is_zero_when_no_answers_exist():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    assert submission.answered_count == 0


def test_submission_answered_count_ignores_empty_answers():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition1 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    definition2 = create_definition(
        questionnaire=questionnaire,
        question_id="3737696",
        question_code="E2",
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Kitöltött válasz",
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
    )

    submission.add_answer(answer1)
    submission.add_answer(answer2)

    assert submission.answered_count == 1


def test_submission_answered_count_counts_all_answered_questions():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition1 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    definition2 = create_definition(
        questionnaire=questionnaire,
        question_id="3737696",
        question_code="E2",
    )

    definition3 = create_definition(
        questionnaire=questionnaire,
        question_id="3737697",
        question_code="E3",
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Első válasz",
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
        text_value="Második válasz",
    )

    answer3 = Answer(
        submission=submission,
        question_definition=definition3,
    )

    submission.add_answer(answer1)
    submission.add_answer(answer2)
    submission.add_answer(answer3)

    assert submission.answered_count == 2

def test_submission_answered_answers_returns_only_answered_answers():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition1 = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    definition2 = create_definition(
        questionnaire=questionnaire,
        question_id="3737696",
        question_code="E2",
    )

    definition3 = create_definition(
        questionnaire=questionnaire,
        question_id="3737697",
        question_code="E3",
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Első válasz",
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
    )

    answer3 = Answer(
        submission=submission,
        question_definition=definition3,
        text_value="Harmadik válasz",
    )

    submission.add_answer(answer1)
    submission.add_answer(answer2)
    submission.add_answer(answer3)

    assert submission.answered_answers == (
        answer1,
        answer3,
    )
def test_submission_answered_answers_is_empty_when_no_answer_is_answered():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    submission.add_answer(answer)

    assert submission.answered_answers == ()
    assert submission.answered_count == 0

def test_submission_has_answer_returns_true_when_answer_exists():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    submission.add_answer(answer)

    assert submission.has_answer("3737695") is True


def test_submission_has_answer_returns_false_when_answer_does_not_exist():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    assert submission.has_answer("3737695") is False


def test_submission_has_answer_rejects_empty_question_id():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    with pytest.raises(ValueError):
        submission.has_answer("")

def test_is_question_answered_returns_true_for_answered_question():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
        text_value="Kitöltött válasz",
    )

    submission.add_answer(answer)

    assert submission.is_question_answered("3737695") is True


def test_is_question_answered_returns_false_for_empty_answer():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    definition = create_definition(
        questionnaire=questionnaire,
        question_id="3737695",
        question_code="E1",
    )

    answer = Answer(
        submission=submission,
        question_definition=definition,
    )

    submission.add_answer(answer)

    assert submission.has_answer("3737695") is True
    assert submission.is_question_answered("3737695") is False


def test_is_question_answered_returns_false_when_answer_does_not_exist():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    assert submission.has_answer("3737695") is False
    assert submission.is_question_answered("3737695") is False


def test_is_question_answered_rejects_empty_question_id():
    questionnaire = create_questionnaire()
    submission = create_submission(questionnaire)

    with pytest.raises(ValueError):
        submission.is_question_answered("")