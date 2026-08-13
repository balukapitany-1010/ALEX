import pytest
from alex.esg.domain.question import Question

def test_question_can_be_created():
    question = Question(
        question_id = "3737696",
        question_code = "E1",
    )
    assert question.question_id == "3737696"
    assert question.question_code == "E1"

def test_question_rejects_empty_question_id():
    with pytest.raises(ValueError):
        Question(
            question_id = "",
            question_code = "E1",
        )
def test_question_rejects_empty_question_code():
    with pytest.raises(ValueError):
        Question(
            question_id = "3737696",
            question_code = "",
        )
