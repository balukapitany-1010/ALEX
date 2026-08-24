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
                question_definition.question_type
                in single_selection_types
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

        self.submission = submission
        self.question_definition = question_definition
        self.selected_options = (
            list(selected_options)
            if selected_options is not None
            else []
        )
        self.text_value = text_value