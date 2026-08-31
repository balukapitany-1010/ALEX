from dataclasses import dataclass
from typing import Any

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)
from alex.esg.services.submission_definition_validator import (
    SubmissionDefinitionValidator,
)


@dataclass(frozen=True)
class QuestionnaireCompatibilityResult:
    definition_version: str
    submission_version: str

    definition_count: int
    response_question_count: int
    matched_question_count: int

    issues: tuple[ImportIssue, ...]

    @property
    def version_matches(self) -> bool:
        return (
            self.definition_version == self.submission_version
        )

    @property
    def errors(self) -> tuple[ImportIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if (issue.severity is ImportIssueSeverity.ERROR)
        )

    @property
    def warnings(self) -> tuple[ImportIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if (issue.severity is ImportIssueSeverity.WARNING)
        )

    @property
    def unknown_question_count(self) -> int:
        return sum(
            1 for issue in self.issues
            if (
                issue.code == "QUESTION_DEFINITION_NOT_FOUND"
            )
        )

    @property
    def question_code_mismatch_count(self) -> int:
        return sum(
            1 for issue in self.issues
            if (
                issue.code == "QUESTION_CODE_MISMATCH"
            )
        )

    @property
    def unknown_option_id_count(self) -> int:
        return sum(
            1 for issue in self.issues
            if (
                issue.code == "UNKNOWN_OPTION_ID"
            )
        )

    @property
    def is_structurally_compatible(self) -> bool:
        return not self.errors


class QuestionnaireCompatibilityService:
    def __init__(
        self,
        definition_validator: (
            SubmissionDefinitionValidator | None
        ) = None,
    ) -> None:
        self._definition_validator = (
            definition_validator
            if definition_validator is not None
            else SubmissionDefinitionValidator()
        )

    def analyze(
        self,
        batch_data: dict[str, Any],
        *,
        questionnaire: Questionnaire,
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> QuestionnaireCompatibilityResult:
        if not isinstance(batch_data, dict):
            raise TypeError("batch_data must be a dictionary")

        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError("questionnaire must be a Questionnaire")

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

        submission_version = (
            self._required_string(
                batch_data,
                "spec_version",
            )
        )

        submissions = batch_data.get("submissions")

        if not isinstance(submissions, list):
            raise ValueError("submissions must be a list")

        definition_ids = {definition.question.question_id for definition in question_definitions}

        issues: list[ImportIssue] = []

        response_question_count = 0
        matched_question_count = 0

        for submission_index, submission_data in enumerate(
            submissions
        ):
            if not isinstance(
                submission_data,
                dict,
            ):
                raise ValueError("submission must be an object")

            response_data = submission_data.get("response")

            if not isinstance(
                response_data,
                dict,
            ):
                raise ValueError("submission response must be an object")

            questions = response_data.get("questions")

            if not isinstance(questions, list):
                raise ValueError("response questions must be a list")

            response_question_count += len(questions)

            for question_data in questions:
                if not isinstance(
                    question_data,
                    dict,
                ):
                    continue

                technical_id = question_data.get("id")

                if (
                    isinstance(technical_id, str)
                    and technical_id.strip() in definition_ids
                ):
                    matched_question_count += 1

            validation_issues = (
                self._definition_validator.validate_questions(
                    response_data,
                    question_definitions=(
                        question_definitions
                    ),
                )
            )

            for issue in validation_issues:
                issues.append(
                    ImportIssue(
                        severity=issue.severity,
                        code=issue.code,
                        message=(
                            f"submission "
                            f"{submission_index}: "
                            f"{issue.message}"
                        ),
                    )
                )

        return QuestionnaireCompatibilityResult(
            definition_version=(questionnaire.spec_version),
            submission_version=(submission_version),
            definition_count=len(question_definitions),
            response_question_count=(response_question_count),
            matched_question_count=(matched_question_count),
            issues=tuple(issues),
        )

    @staticmethod
    def _required_string(
        data: dict[str, Any],
        key: str,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string")

        normalized = value.strip()

        if not normalized:
            raise ValueError(f"{key} cannot be empty")

        return normalized