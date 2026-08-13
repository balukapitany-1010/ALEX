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
        organization: str,
        organization_sizes: list [str],
        geographical_relevance: list [str],
        topic: str,
        subtopic: str | None = None,
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

        if not isinstance(organization, str):
            raise TypeError("organization must be a string")

        if not organization.strip():
            raise ValueError("organization cannot be empty")

        if not isinstance(organization_sizes, list):
            raise TypeError("organization_sizes must be a list")

        if not all(isinstance(value, str) for value in organization_sizes):
            raise TypeError("organization_sizes must contain only strings")

        if not isinstance(geographical_relevance, list):
            raise TypeError("geographical_relevance must be a list")

        if not all(
                isinstance(value, str)
                for value in geographical_relevance
        ):
            raise TypeError(
                "geographical_relevance must contain only strings"
            )

        if not isinstance(topic, str):
            raise TypeError("topic must be a string")

        if not topic.strip():
            raise ValueError("topic cannot be empty")

        if subtopic is not None and not isinstance(subtopic, str):
            raise TypeError("subtopic must be a string or None")
        if subtopic is not None and not subtopic.strip():
            raise ValueError("subtopic cannot be empty")

        self.question = question
        self.questionnaire = questionnaire
        self.title = title
        self.category = category
        self.subject = subject
        self.organization = organization
        self.organization_sizes = list(organization_sizes)
        self.geographical_relevance = list(geographical_relevance)
        self.topic = topic
        self.subtopic = subtopic