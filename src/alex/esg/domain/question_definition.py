from alex.esg.domain.question import Question
from alex.esg.domain.questionnaire import Questionnaire


class QuestionDefinition:
    def __init__(
        self,
        question: Question,
        questionnaire: Questionnaire,
        title: str,
    ):
        if not isinstance(question, Question):
            raise TypeError("question must be a Question")

        if not isinstance(questionnaire, Questionnaire):
            raise TypeError("questionnaire must be a Questionnaire")

        if not isinstance(title, str):
            raise TypeError("title must be a string")

        if not title.strip():
            raise ValueError("title cannot be empty")

        self.question = question
        self.questionnaire = questionnaire
        self.title = title