from uuid import uuid4

from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.submission import Submission
from alex.esg.domain.option import Option


class Answer:
    def __init__(
        self,
        submission: Submission,
        question_definition: QuestionDefinition,
        selected_options: list[Option] | None = None,
        text_value: str | None = None,
        number_value: int | float | None = None,
    ):
        if not isinstance(submission, Submission):
            raise TypeError("submission must be a Submission")

        if not isinstance(question_definition, QuestionDefinition):
            raise TypeError(
                "question_definition must be a QuestionDefinition"
            )

        # selected_options validáció
        if selected_options is not None:
            if not isinstance(selected_options, list):
                raise TypeError(
                    "selected_options must be a list or None"
                )

            if not all(
                isinstance(option, Option)
                for option in selected_options
            ):
                raise TypeError(
                    "selected_options must contain only Option objects"
                )

            allowed_option_ids = {
                option.option_id
                for option in question_definition.options
            }

            selected_option_ids = {
                option.option_id
                for option in selected_options
            }

            if not selected_option_ids.issubset(allowed_option_ids):
                raise ValueError(
                    "selected_options must belong to the QuestionDefinition"
                )

            single_selection_types = {
                QuestionType.RADIO,
                QuestionType.DROPDOWN,
            }

            if (
                question_definition.question_type in single_selection_types
                and len(selected_options) > 1
            ):
                raise ValueError(
                    f"{question_definition.question_type.value} "
                    "questions can have at most one option"
                )

            non_option_types = {
                QuestionType.TEXT,
                QuestionType.COMMENT,
                QuestionType.NUMBER,
            }

            if (
                question_definition.question_type in non_option_types
                and selected_options
            ):
                raise ValueError(
                    f"{question_definition.question_type.value} "
                    "questions cannot have selected options"
                )

        # text_value validáció
        if text_value is not None:
            if not isinstance(text_value, str):
                raise TypeError(
                    "text_value must be a string or None"
                )

            if not text_value.strip():
                raise ValueError(
                    "text_value cannot be empty"
                )

            text_value_types = {
                QuestionType.TEXT,
                QuestionType.COMMENT,
                QuestionType.MIXED,
            }

            if (
                question_definition.question_type
                not in text_value_types
            ):
                raise ValueError(
                    f"{question_definition.question_type.value} "
                    "questions cannot have text_value"
                )

        # number_value validáció
        if number_value is not None:
            if isinstance(number_value, bool) or not isinstance(
                number_value,
                (int, float),
            ):
                raise TypeError(
                    "number_value must be an int, float or None"
                )

        number_value_types = {
            QuestionType.NUMBER,
            QuestionType.MIXED,
        }

        if (
            number_value is not None
            and question_definition.question_type not in number_value_types
        ):
            raise ValueError(
                f"{question_definition.question_type.value} "
                "questions cannot have number_value"
            )

        if (submission.questionnaire.questionnaire_key != question_definition.questionnaire.questionnaire_key):
            raise ValueError(
                "question_definition must belong to the same questionnaire as the submission"
            )

        # Objektum állapotának beállítása
        self.submission = submission
        self.question_definition = question_definition
        self.selected_options = (
            list(selected_options)
            if selected_options is not None
            else []
        )
        self.text_value = text_value
        self.number_value = number_value
        self.answer_id = str(uuid4())

    @property
    def is_answered(self) -> bool:
        if self.question_definition.question_type in {
            QuestionType.RADIO,
            QuestionType.DROPDOWN,
            QuestionType.CHECKBOX,
        }:
            return bool(self.selected_options)

        if self.question_definition.question_type in {
            QuestionType.TEXT,
            QuestionType.COMMENT,
        }:
            return self.text_value is not None

        if self.question_definition.question_type == QuestionType.NUMBER:
            return self.number_value is not None

        if self.question_definition.question_type == QuestionType.MIXED:
            return (
                bool(self.selected_options)
                or self.text_value is not None
                or self.number_value is not None
            )

        return False

    @property
    def answer_key(self) -> str:
        return (
            f"{self.submission.submission_id}:"
            f"{self.question_definition.question.question_id}"
        )