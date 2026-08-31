from dataclasses import dataclass
from typing import Any
from alex.esg.domain.question_definition import  QuestionDefinition
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)
from alex.esg.services.submission_batch_importer import SubmissionBatchImporter
from alex.esg.services.submission_definition_validator import SubmissionDefinitionValidator
from alex.esg.services.submission_json_importer import SubmissionJsonImporter


@dataclass(frozen=True)
class SubmissionBatchJsonItemResult:
    index: int
    submission: Submission | None
    issues: tuple[ImportIssue, ...]

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
            if (
                issue.severity
                is ImportIssueSeverity.WARNING
            )
        )

    @property
    def is_imported(self) -> bool:
        return (
                self.submission is not None and not self.errors
        )


@dataclass(frozen=True)
class SubmissionBatchJsonImportResult:
    spec_version: str
    batch_id: str | None
    items: tuple[
        SubmissionBatchJsonItemResult,
        ...
    ]
    issues: tuple[ImportIssue, ...]

    @property
    def submissions(
        self,
    ) -> tuple[Submission, ...]:
        return tuple(
            item.submission for item in self.items if item.submission is not None
        )

    @property
    def errors(self) -> tuple[ImportIssue, ...]:
        result: list[ImportIssue] = []

        result.extend(
            issue
            for issue in self.issues
            if (
                issue.severity is ImportIssueSeverity.ERROR
            )
        )

        for item in self.items:result.extend(item.errors)

        return tuple(result)

    @property
    def warnings(self) -> tuple[ImportIssue, ...]:
        result: list[ImportIssue] = []

        result.extend(
            issue
            for issue in self.issues
            if (
                issue.severity is ImportIssueSeverity.WARNING
            )
        )

        for item in self.items: result.extend(item.warnings)

        return tuple(result)

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def imported_count(self) -> int:
        return sum(
            1 for item in self.items if item.is_imported
        )

    @property
    def failed_count(self) -> int:
        return (
            self.total_count - self.imported_count
        )

    @property
    def is_successful(self) -> bool:
        return not self.errors


class SubmissionBatchJsonImporter:
    def __init__(
        self,
        *,
        batch_inspector: SubmissionBatchImporter,
        definition_validator: (
            SubmissionDefinitionValidator
        ),
        submission_importer: SubmissionJsonImporter,
    ) -> None:
        if not isinstance(
            batch_inspector,
            SubmissionBatchImporter,
        ):
            raise TypeError(
                "batch_inspector must be a "
                "SubmissionBatchImporter"
            )

        if not isinstance(
            definition_validator,
            SubmissionDefinitionValidator,
        ):
            raise TypeError(
                "definition_validator must be a "
                "SubmissionDefinitionValidator"
            )

        if not isinstance(
            submission_importer,
            SubmissionJsonImporter,
        ):
            raise TypeError(
                "submission_importer must be a "
                "SubmissionJsonImporter"
            )

        self._batch_inspector = batch_inspector
        self._definition_validator = (
            definition_validator
        )
        self._submission_importer = (
            submission_importer
        )

    def import_batch(
        self,
        batch_data: dict[str, Any],
        *,
        questionnaire: Questionnaire,
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> SubmissionBatchJsonImportResult:
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

        inspection = (
            self._batch_inspector.inspect_batch(
                batch_data
            )
        )

        submissions_data = batch_data.get("submissions")

        if not isinstance(submissions_data, list):
            raise ValueError("submissions must be a list")

        if (
                inspection.spec_version
                != questionnaire.spec_version
        ):
            version_issue = ImportIssue(
                severity=ImportIssueSeverity.ERROR,
                code="QUESTIONNAIRE_VERSION_MISMATCH",
                message=(
                    "questionnaire definition version "
                    f"{questionnaire.spec_version} "
                    "does not match submission "
                    f"version "
                    f"{inspection.spec_version}"
                ),
            )

            items = tuple(
                SubmissionBatchJsonItemResult(
                    index=item.index,
                    submission=None,
                    issues=(),
                )
                for item in inspection.items
            )

            return SubmissionBatchJsonImportResult(
                spec_version=inspection.spec_version,
                batch_id=inspection.batch_id,
                items=items,
                issues=(version_issue,),
            )

        results: list[
            SubmissionBatchJsonItemResult
        ] = []

        for inspection_item in inspection.items:
            item_issues = list(inspection_item.issues)

            if self._has_errors(item_issues):
                results.append(
                    SubmissionBatchJsonItemResult(
                        index=inspection_item.index,
                        submission=None,
                        issues=tuple(item_issues),
                    )
                )

                continue

            submission_data = submissions_data[inspection_item.index]

            response_data = submission_data.get("response")

            if not isinstance(
                response_data,
                dict,
            ):
                item_issues.append(
                    ImportIssue(
                        severity=(
                            ImportIssueSeverity.ERROR
                        ),
                        code="INVALID_RESPONSE_STRUCTURE",
                        message=(
                            "submission response "
                            "must be an object"
                        ),
                    )
                )

                results.append(
                    SubmissionBatchJsonItemResult(
                        index=inspection_item.index,
                        submission=None,
                        issues=tuple(item_issues),
                    )
                )

                continue

            definition_issues = (
                self._definition_validator.validate_questions(
                    response_data,
                    question_definitions=(
                        question_definitions
                    ),
                )
            )

            item_issues.extend(definition_issues)

            if self._has_errors(item_issues):
                results.append(
                    SubmissionBatchJsonItemResult(
                        index=inspection_item.index,
                        submission=None,
                        issues=tuple(item_issues),
                    )
                )

                continue

            try:
                submission = (
                    self._submission_importer.import_submission(
                        submission_data,
                        spec_version=(
                            inspection.spec_version
                        ),
                        questionnaire=questionnaire,
                        question_definitions=(
                            question_definitions
                        ),
                    )
                )

            except (TypeError, ValueError) as error:
                item_issues.append(
                    ImportIssue(
                        severity=(
                            ImportIssueSeverity.ERROR
                        ),
                        code="SUBMISSION_IMPORT_FAILED",
                        message=str(error),
                    )
                )

                submission = None

            results.append(
                SubmissionBatchJsonItemResult(
                    index=inspection_item.index,
                    submission=submission,
                    issues=tuple(item_issues),
                )
            )

        return SubmissionBatchJsonImportResult(
            spec_version=inspection.spec_version,
            batch_id=inspection.batch_id,
            items=tuple(results),
            issues=(),
        )

    @staticmethod
    def _has_errors(
        issues: list[ImportIssue],
    ) -> bool:
        return any(
            issue.severity is ImportIssueSeverity.ERROR for issue in issues
        )