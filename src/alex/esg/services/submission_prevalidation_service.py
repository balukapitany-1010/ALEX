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
from alex.esg.services.submission_batch_importer import (
    SubmissionBatchImporter,
    SubmissionBatchResult,
)
from alex.esg.services.submission_definition_validator import (SubmissionDefinitionValidator)


@dataclass(frozen=True)
class SubmissionPrevalidationResult:
    batch_result: SubmissionBatchResult
    issues: tuple[ImportIssue, ...]

    @property
    def errors(self) -> tuple[ImportIssue, ...]:
        return tuple(issue for issue in self.issues
            if (
                issue.severity is ImportIssueSeverity.ERROR
            )
        )

    @property
    def warnings(self) -> tuple[ImportIssue, ...]:
        return tuple(issue for issue in self.issues
            if (
                issue.severity is ImportIssueSeverity.WARNING
            )
        )

    @property
    def is_valid(self) -> bool:
        if self.errors:
            return False

        return all(item.is_valid for item in self.batch_result.items)


class SubmissionPrevalidationService:
    def __init__(
        self,
        batch_importer: SubmissionBatchImporter | None = None,
        definition_validator: (
            SubmissionDefinitionValidator | None
        ) = None,
    ) -> None:
        self._batch_importer = (
            batch_importer
            if batch_importer is not None
            else SubmissionBatchImporter()
        )

        self._definition_validator = (
            definition_validator
            if definition_validator is not None
            else SubmissionDefinitionValidator()
        )

    def validate(
        self,
        batch_data: dict[str, Any],
        *,
        questionnaire: Questionnaire,
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> SubmissionPrevalidationResult:
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

        batch_result = ( self._batch_importer.inspect_batch( batch_data))

        issues: list[ImportIssue] = []

        if (
            batch_result.spec_version != questionnaire.spec_version
        ):
            issues.append(
                ImportIssue(
                    severity=(
                        ImportIssueSeverity.ERROR
                    ),
                    code=(
                        "QUESTIONNAIRE_VERSION_MISMATCH"
                    ),
                    message=(
                        "questionnaire definition version "
                        f"{questionnaire.spec_version} "
                        "does not match submission "
                        f"version "
                        f"{batch_result.spec_version}"
                    ),
                )
            )

            return SubmissionPrevalidationResult(
                batch_result=batch_result,
                issues=tuple(issues),
            )

        submissions = batch_data.get(
            "submissions"
        )

        if not isinstance(submissions, list):
            return SubmissionPrevalidationResult(
                batch_result=batch_result,
                issues=tuple(issues),
            )

        for submission_index, submission_data in enumerate(
            submissions
        ):
            if not isinstance(submission_data,dict,):
                continue

            response_data = submission_data.get("response")

            if not isinstance(response_data,dict,):
                continue

            definition_issues = (
                self._definition_validator.validate_questions(
                    response_data,
                    question_definitions=(
                        question_definitions
                    ),
                )
            )

            for issue in definition_issues:
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

        return SubmissionPrevalidationResult(
            batch_result=batch_result,
            issues=tuple(issues),
        )