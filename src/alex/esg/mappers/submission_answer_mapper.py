from typing import Any
from alex.esg.domain.answer import Answer
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.submission import Submission
from alex.esg.domain.answer_value import AnswerValue


class SubmissionAnswerMapper:
    _SUPPORTED_FIELD_TYPES = {
        "single",
        "multi",
        "text",
        "number",
    }

    def map_values(
        self,
        question_data: dict[str, Any],
    ) -> tuple[AnswerValue, ...]:
        if not isinstance(question_data, dict):
            raise TypeError(
                "question_data must be a dictionary"
            )

        fields = question_data.get("fields")

        if not isinstance(fields, list):
            raise ValueError(
                "question fields must be a list"
            )

        result: list[AnswerValue] = []

        for field in fields:
            result.extend(
                self._map_field(field)
            )

        return tuple(result)

    def _map_field(
        self,
        field: Any,
    ) -> list[AnswerValue]:
        if not isinstance(field, dict):
            raise ValueError(
                "field must be an object"
            )

        field_type = field.get("type")

        if not isinstance(field_type, str):
            raise ValueError(
                "field type must be a string"
            )

        field_type = field_type.strip().lower()

        if (
            field_type
            not in self._SUPPORTED_FIELD_TYPES
        ):
            raise ValueError(
                f"unsupported field type: {field_type}"
            )

        values = field.get("values")

        if not isinstance(values, list):
            raise ValueError(
                "field values must be a list"
            )

        result: list[AnswerValue] = []

        for value_data in values:
            result.append(
                self._map_value(
                    field_type=field_type,
                    value_data=value_data,
                )
            )

        return result

    def _map_value(
        self,
        *,
        field_type: str,
        value_data: Any,
    ) -> AnswerValue:
        if not isinstance(value_data, dict):
            raise ValueError(
                "field value must be an object"
            )

        option_id = self._optional_option_id(
            value_data.get("optionId")
        )

        if field_type in {
            "single",
            "multi",
        }:
            if option_id is None:
                raise ValueError(
                    f"{field_type} value "
                    "must have optionId"
                )

            selected = value_data.get(
                "selected"
            )

            if not isinstance(selected, bool):
                raise ValueError(
                    f"{field_type} value "
                    "selected must be a bool"
                )

            return AnswerValue(
                field_type=field_type,
                option_id=option_id,
                selected=selected,
            )

        if field_type == "text":
            value = value_data.get(
                "value"
            )

            if (
                value is not None
                and not isinstance(value, str)
            ):
                raise ValueError(
                    "text value must be "
                    "a string or None"
                )

            return AnswerValue(
                field_type="text",
                option_id=option_id,
                text_value=value,
            )

        if field_type == "number":
            value = value_data.get(
                "value"
            )

            if value is not None:
                if (
                    isinstance(value, bool)
                    or not isinstance(
                        value,
                        (int, float),
                    )
                ):
                    raise ValueError(
                        "number value must be "
                        "an int, float or None"
                    )

            return AnswerValue(
                field_type="number",
                option_id=option_id,
                number_value=value,
            )

        raise ValueError(
            f"unsupported field type: {field_type}"
        )

    def map_answer(
            self,
            question_data: dict[str, Any],
            *,
            submission: Submission,
            question_definitions: tuple[
                QuestionDefinition,
                ...
            ],
    ) -> Answer:
        if not isinstance(submission, Submission):
            raise TypeError(
                "submission must be a Submission"
            )

        if not isinstance(
                question_definitions,
                tuple,
        ):
            raise TypeError(
                "question_definitions must be a tuple"
            )

        if not all(
                isinstance(
                    definition,
                    QuestionDefinition,
                )
                for definition in question_definitions
        ):
            raise TypeError(
                "question_definitions must contain "
                "only QuestionDefinition objects"
            )

        technical_id = self._required_string(
            question_data,
            "id",
        )

        question_definition = (
            self._find_question_definition(
                technical_id=technical_id,
                question_definitions=(
                    question_definitions
                ),
            )
        )

        values = self.map_values(
            question_data
        )

        return Answer(
            submission=submission,
            question_definition=(
                question_definition
            ),
            values=list(values),
        )

    def map_answers(
            self,
            response_data: dict[str, Any],
            *,
            submission: Submission,
            question_definitions: tuple[
                QuestionDefinition,
                ...
            ],
    ) -> tuple[Answer, ...]:
        if not isinstance(response_data, dict):
            raise TypeError(
                "response_data must be a dictionary"
            )

        if not isinstance(submission, Submission):
            raise TypeError(
                "submission must be a Submission"
            )

        if not isinstance(
                question_definitions,
                tuple,
        ):
            raise TypeError(
                "question_definitions must be a tuple"
            )

        if not all(
                isinstance(
                    definition,
                    QuestionDefinition,
                )
                for definition in question_definitions
        ):
            raise TypeError(
                "question_definitions must contain "
                "only QuestionDefinition objects"
            )

        questions = response_data.get(
            "questions"
        )

        if not isinstance(questions, list):
            raise ValueError(
                "response questions must be a list"
            )

        seen_question_ids: set[str] = set()

        for question_data in questions:
            if not isinstance(
                    question_data,
                    dict,
            ):
                raise ValueError(
                    "response question must be an object"
                )

            technical_id = self._required_string(
                question_data,
                "id",
            )

            if technical_id in seen_question_ids:
                raise ValueError(
                    "duplicate response question id: "
                    f"{technical_id}"
                )

            seen_question_ids.add(
                technical_id
            )

        answers: list[Answer] = []

        for question_data in questions:
            answer = self.map_answer(
                question_data,
                submission=submission,
                question_definitions=(
                    question_definitions
                ),
            )

            answers.append(answer)

        return tuple(answers)

    @staticmethod
    def _find_question_definition(
            *,
            technical_id: str,
            question_definitions: tuple[
                QuestionDefinition,
                ...
            ],
    ) -> QuestionDefinition:
        for definition in question_definitions:
            if (
                    definition.question.question_id
                    == technical_id
            ):
                return definition

        raise ValueError(
            "question definition not found "
            f"for technical id: {technical_id}"
        )

    @staticmethod
    def _required_string(
            data: dict[str, Any],
            key: str,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str):
            raise ValueError(
                f"{key} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{key} cannot be empty"
            )

        return normalized

    @staticmethod
    def _optional_option_id(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "optionId must be "
                "a string or None"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "optionId cannot be empty"
            )

        return normalized