from alex.esg.domain.question import Question
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.option import Option


class QuestionDefinition:
    def __init__(
        self,
        question: Question,
        questionnaire: Questionnaire,
        title: str,
        category: QuestionCategory,
        subject: str,
        organization: str,
        organization_sizes: list[str],
        geographical_relevance: list[str],
        topic: str,
        question_type: QuestionType,
        subtopic: str | None = None,
        requirement: str | None = None,
        options: list[Option] | None = None,
    ):
        if not isinstance(question, Question):
            raise TypeError("question must be a Question")

        if not isinstance(questionnaire, Questionnaire):
            raise TypeError("questionnaire must be a Questionnaire")

        if not isinstance(title, str):
            raise TypeError("title must be a string")

        if not title.strip():
            raise ValueError("title cannot be empty")

        if not isinstance(category, QuestionCategory):
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
            raise TypeError(
                "organization_sizes must contain only strings"
            )

        if not isinstance(geographical_relevance, list):
            raise TypeError(
                "geographical_relevance must be a list"
            )

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
            raise TypeError(
                "subtopic must be a string or None"
            )

        if subtopic is not None and not subtopic.strip():
            raise ValueError("subtopic cannot be empty")

        if not isinstance(question_type, QuestionType):
            raise TypeError(
                "question_type must be a QuestionType"
            )

        if requirement is not None and not isinstance(requirement, str):
            raise TypeError(
                "requirement must be a string or None"
            )

        if requirement is not None and not requirement.strip():
            raise ValueError("requirement cannot be empty")

        # options validáció
        if options is not None:
            if not isinstance(options, list):
                raise TypeError(
                    "options must be a list or None"
                )

            if not all(
                isinstance(option, Option)
                for option in options
            ):
                raise TypeError(
                    "options must contain only Option objects"
                )

        # Ezekhez a kérdéstípusokhoz kötelező legalább egy option
        option_required_types = {
            QuestionType.RADIO,
            QuestionType.CHECKBOX,
            QuestionType.DROPDOWN,
        }

        if question_type in option_required_types and not options:
            raise ValueError(
                f"{question_type.value} question "
                "must have at least one option"
            )

        self.question = question
        self.questionnaire = questionnaire
        self.title = title
        self.category = category
        self.subject = subject
        self.organization = organization
        self.organization_sizes = list(organization_sizes)
        self.geographical_relevance = list(
            geographical_relevance
        )
        self.topic = topic
        self.subtopic = subtopic
        self.question_type = question_type
        self.requirement = requirement
        self.options = list(options) if options is not None else []