from alex.esg.domain.question import Question
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.question_category import QuestionCategory


class QuestionDefinition:
    def __init__(
        self,
        question: Question,
        questionnaire: Questionnaire,
        title: str,
        category: QuestionCategory,
        subject: str,
    ):
        if not isinstance(question, Question):
            raise TypeError("question must be a Question")

        if not isinstance(questionnaire, Questionnaire):
            raise TypeError("questionnaire must be a Questionnaire")

        if not isinstance(title, str):
            raise TypeError("title must be a string")

        if not title.strip():
            raise ValueError("title cannot be empty")

        if  not isinstance(category, QuestionCategory):
            raise TypeError("category must be a QuestionCategory")

        if not isinstance(subject, str):
            raise TypeError("subject must be a string")

        if not subject.strip():
            raise ValueError("subject cannot be empty")

        self.question = question
        self.questionnaire = questionnaire
        self.title = title
        self.category = category
        self.subject = subject