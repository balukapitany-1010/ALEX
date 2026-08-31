from typing import Any

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)


class SubmissionDefinitionValidator:
    def validate_questions(
        self,
        response_data: dict[str, Any],
        *,
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> tuple[ImportIssue, ...]:
        if not isinstance(response_data, dict):
            raise TypeError("response_data must be a dictionary")

        if not isinstance(
            question_definitions,
            tuple,
        ):
            raise TypeError("question_definitions must be a tuple")

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
            raise ValueError("response questions must be a list")

        definitions_by_id = {
            definition.question.question_id:
            definition
            for definition in question_definitions
        }

        issues: list[ImportIssue] = []

        for question_data in questions:
            if not isinstance(
                question_data,
                dict,
            ):
                continue

            technical_id = question_data.get("id")

            if (
                not isinstance(technical_id, str)
                or not technical_id.strip()
            ):
                continue

            technical_id = technical_id.strip()

            definition = definitions_by_id.get(
                technical_id
            )

            if definition is None:
                issues.append(
                    ImportIssue(
                        severity=(
                            ImportIssueSeverity.ERROR
                        ),
                        code=(
                            "QUESTION_DEFINITION_NOT_FOUND"
                        ),
                        message=(
                            "question definition not found "
                            f"for technical id: "
                            f"{technical_id}"
                        ),
                    )
                )

                continue

            response_question_code = (
                question_data.get(
                    "question_id"
                )
            )

            if (
                isinstance(
                    response_question_code,
                    str,
                )
                and response_question_code.strip()
            ):
                response_question_code = (
                    response_question_code.strip()
                )

                definition_question_code = (
                    definition.question.question_code
                )

                if (
                    response_question_code
                    != definition_question_code
                ):
                    issues.append(
                        ImportIssue(
                            severity=(
                                ImportIssueSeverity.WARNING
                            ),
                            code=(
                                "QUESTION_CODE_MISMATCH"
                            ),
                            message=(
                                "question code mismatch "
                                f"for technical id "
                                f"{technical_id}: "
                                f"definition="
                                f"{definition_question_code}, "
                                f"response="
                                f"{response_question_code}"
                            ),
                        )
                    )

            option_issues = (
                self._validate_option_ids(
                    question_data=question_data,
                    definition=definition,
                )
            )

            issues.extend(option_issues)

        return tuple(issues)

    @staticmethod
    def _validate_option_ids(
        *,
        question_data: dict[str, Any],
        definition: QuestionDefinition,
    ) -> tuple[ImportIssue, ...]:
        issues: list[ImportIssue] = []

        fields = question_data.get("fields")

        if not isinstance(fields, list):
            return ()

        allowed_value_ids = set(
            definition.allowed_value_ids
        )

        for field_index, field in enumerate(
            fields
        ):
            if not isinstance(
                field,
                dict,
            ):
                continue

            values = field.get("values")

            if not isinstance(values, list):
                continue

            for value_index, value_data in enumerate(values):
                if not isinstance(
                    value_data,
                    dict,
                ):
                    continue

                option_id = value_data.get("optionId")

                if option_id is None:
                    continue

                if not isinstance(
                    option_id,
                    str,
                ):
                    issues.append(
                        ImportIssue(
                            severity=(
                                ImportIssueSeverity.ERROR
                            ),
                            code=(
                                "INVALID_OPTION_ID"
                            ),
                            message=(
                                "optionId must be a string "
                                f"for question "
                                f"{definition.question.question_id}, "
                                f"field {field_index}, "
                                f"value {value_index}"
                            ),
                        )
                    )

                    continue

                option_id = option_id.strip()

                if not option_id:
                    issues.append(
                        ImportIssue(
                            severity=(
                                ImportIssueSeverity.ERROR
                            ),
                            code=(
                                "INVALID_OPTION_ID"
                            ),
                            message=(
                                "optionId cannot be empty "
                                f"for question "
                                f"{definition.question.question_id}"
                            ),
                        )
                    )

                    continue

                if (option_id not in allowed_value_ids
                ):
                    issues.append(
                        ImportIssue(
                            severity=(
                                ImportIssueSeverity.ERROR
                            ),
                            code=(
                                "UNKNOWN_OPTION_ID"
                            ),
                            message=(
                                "unknown optionId "
                                f"{option_id} "
                                f"for question "
                                f"{definition.question.question_id}"
                            ),
                        )
                    )

        return tuple(issues)