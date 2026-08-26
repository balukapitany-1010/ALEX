from datetime import datetime, timezone
from uuid import uuid4

from alex.esg.domain.option import Option
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.submission import Submission


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


        if (
            submission.questionnaire.questionnaire_key
            != question_definition.questionnaire.questionnaire_key
        ):
            raise ValueError(
                "question_definition must belong to the same "
                "questionnaire as the submission"
            )



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
                    "selected_options must belong to the "
                    "QuestionDefinition"
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
                question_definition.question_type
                in non_option_types
                and selected_options
            ):
                raise ValueError(
                    f"{question_definition.question_type.value} "
                    "questions cannot have selected options"
                )



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
            and question_definition.question_type
            not in number_value_types
        ):
            raise ValueError(
                f"{question_definition.question_type.value} "
                "questions cannot have number_value"
            )



        self._answer_id = str(uuid4())

        self._submission = submission
        self._question_definition = question_definition

        self._selected_options = (
            list(selected_options)
            if selected_options is not None
            else []
        )

        self._text_value = text_value
        self._number_value = number_value

        now = datetime.now(timezone.utc)

        self._created_at = now
        self._updated_at = now



    @property
    def selected_options(self) -> tuple[Option, ...]:
        return tuple(self._selected_options)

    @property
    def text_value(self) -> str | None:
        return self._text_value

    @property
    def number_value(self) -> int | float | None:
        return self._number_value
    @property
    def submission(self) -> Submission:
        return self._submission
    @property
    def question_definition(self) -> QuestionDefinition:
        return self._question_definition
    @property
    def answer_id(self) -> str:
        return self._answer_id
    @property
    def created_at(self) -> datetime:
        return self._created_at
    @property
    def updated_at(self) -> datetime:
        return self._updated_at




    @property
    def is_answered(self) -> bool:
        question_type = self.question_definition.question_type

        if question_type in {
            QuestionType.RADIO,
            QuestionType.DROPDOWN,
            QuestionType.CHECKBOX,
        }:
            return bool(self._selected_options)

        if question_type in {
            QuestionType.TEXT,
            QuestionType.COMMENT,
        }:
            return self._text_value is not None

        if question_type == QuestionType.NUMBER:
            return self._number_value is not None

        if question_type == QuestionType.MIXED:
            return (
                bool(self._selected_options)
                or self._text_value is not None
                or self._number_value is not None
            )

        return False



    @property
    def answer_key(self) -> str:
        return (
            f"{self.submission.submission_id}:"
            f"{self.question_definition.question.question_id}"
        )



    def set_text_value(
        self,
        text_value: str | None,
    ) -> None:
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
            text_value is not None
            and self.question_definition.question_type
            not in text_value_types
        ):
            raise ValueError(
                f"{self.question_definition.question_type.value} "
                "questions cannot have text_value"
            )

        if self._text_value == text_value:
            return

        self._text_value = text_value
        self._updated_at = datetime.now(timezone.utc)



    def set_number_value(
        self,
        number_value: int | float | None,
    ) -> None:
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
            and self.question_definition.question_type
            not in number_value_types
        ):
            raise ValueError(
                f"{self.question_definition.question_type.value} "
                "questions cannot have number_value"
            )

        if self._number_value == number_value:
            return

        self._number_value = number_value
        self._updated_at = datetime.now(timezone.utc)



    def select_option(
        self,
        option: Option,
    ) -> None:
        if not isinstance(option, Option):
            raise TypeError(
                "option must be an Option"
            )

        option_types = {
            QuestionType.RADIO,
            QuestionType.DROPDOWN,
            QuestionType.CHECKBOX,
            QuestionType.MIXED,
        }

        if (
            self.question_definition.question_type
            not in option_types
        ):
            raise ValueError(
                f"{self.question_definition.question_type.value} "
                "questions cannot have selected options"
            )

        allowed_option_ids = {
            allowed_option.option_id
            for allowed_option
            in self.question_definition.options
        }

        if option.option_id not in allowed_option_ids:
            raise ValueError(
                "option must belong to the QuestionDefinition"
            )

        single_selection_types = {
            QuestionType.RADIO,
            QuestionType.DROPDOWN,
        }


        if (
            self.question_definition.question_type
            in single_selection_types
        ):
            if (
                len(self._selected_options) == 1
                and self._selected_options[0].option_id
                == option.option_id
            ):
                return

            self._selected_options = [option]
            self._updated_at = datetime.now(timezone.utc)
            return


        if any(
            selected.option_id == option.option_id
            for selected in self._selected_options
        ):
            return

        self._selected_options.append(option)
        self._updated_at = datetime.now(timezone.utc)



    def unselect_option(
        self,
        option: Option,
    ) -> None:
        if not isinstance(option, Option):
            raise TypeError(
                "option must be an Option"
            )

        allowed_option_ids = {
            allowed_option.option_id
            for allowed_option
            in self.question_definition.options
        }

        if option.option_id not in allowed_option_ids:
            raise ValueError(
                "option must belong to the QuestionDefinition"
            )

        for selected_option in self._selected_options:
            if selected_option.option_id == option.option_id:
                self._selected_options.remove(selected_option)
                self._updated_at = datetime.now(timezone.utc)
                return