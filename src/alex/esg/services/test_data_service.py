from alex.esg.domain.answer import Answer
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.submission import Submission


def add_test_answers(
    submission: Submission,
) -> None:
    question1 = Question(
        question_id="E_TEST_001",
        question_code="E_TEST_001",
    )

    definition1 = QuestionDefinition(
        question=question1,
        questionnaire=submission.questionnaire,
        title=(
            "Rendelkezik a vállalat "
            "környezetvédelmi szabályzattal?"
        ),
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Környezeti irányítás",
        question_type=QuestionType.TEXT,
    )

    answer1 = Answer(
        submission=submission,
        question_definition=definition1,
        text_value="Igen, rendelkezik.",
    )

    submission.add_answer(answer1)

    question2 = Question(
        question_id="E_TEST_002",
        question_code="E_TEST_002",
    )

    definition2 = QuestionDefinition(
        question=question2,
        questionnaire=submission.questionnaire,
        title="Éves energiafelhasználás",
        category=QuestionCategory.E,
        subject="Környezeti fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Energia",
        question_type=QuestionType.NUMBER,
    )

    answer2 = Answer(
        submission=submission,
        question_definition=definition2,
        number_value=1250,
    )

    submission.add_answer(answer2)