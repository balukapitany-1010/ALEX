from dataclasses import dataclass
from typing import Any
from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)

from alex.esg.mappers.submission_header_mapper import (
    SubmissionHeaderData,
    SubmissionHeaderMapper,
)


@dataclass(frozen=True)
class SubmissionBatchItemResult:
    index: int
    header: SubmissionHeaderData | None
    issues: tuple[ImportIssue, ...]

    @property
    def errors(self) -> tuple[str, ...]:
        return tuple(
            issue.message
            for issue in self.issues
            if issue.severity == ImportIssueSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[str, ...]:
        return tuple(
            issue.message
            for issue in self.issues
            if issue.severity == ImportIssueSeverity.WARNING
        )

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class SubmissionBatchResult:
    spec_version: str
    batch_id: str | None
    items: tuple[SubmissionBatchItemResult, ...]

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def valid_count(self) -> int:
        return sum(
            1
            for item in self.items
            if item.is_valid
        )

    @property
    def invalid_count(self) -> int:
        return self.total_count - self.valid_count


class SubmissionBatchImporter:
    def __init__(
        self,
        header_mapper: SubmissionHeaderMapper | None = None,
    ) -> None:
        self._header_mapper = (
            header_mapper
            if header_mapper is not None
            else SubmissionHeaderMapper()
        )

    def inspect_batch(
        self,
        data: dict[str, Any],
    ) -> SubmissionBatchResult:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        spec_version = self._required_string(
            data,
            "spec_version",
        )

        batch_id = self._optional_string(data.get("batch_id"))

        submissions = data.get("submissions")

        if not isinstance(submissions, list):
            raise ValueError("submissions must be a list")

        items: list[SubmissionBatchItemResult] = []

        for index, submission_data in enumerate(submissions):
            item = self._inspect_submission(
                index=index,
                submission_data=submission_data,
            )

            items.append(item)

        return SubmissionBatchResult(
            spec_version=spec_version,
            batch_id=batch_id,
            items=tuple(items),
        )

    def _inspect_submission(
            self,
            *,
            index: int,
            submission_data: Any,
    ) -> SubmissionBatchItemResult:
        if not isinstance(
                submission_data,
                dict,
        ):
            return SubmissionBatchItemResult(
                index=index,
                header=None,
                issues=(
                    ImportIssue(
                        severity=ImportIssueSeverity.ERROR,
                        code="INVALID_SUBMISSION_STRUCTURE",
                        message="submission must be an object",
                    ),
                ),
            )

        try:
            header = self._header_mapper.map(
                submission_data
            )

        except (TypeError, ValueError) as error:
            return SubmissionBatchItemResult(
                index=index,
                header=None,
                issues=(
                    ImportIssue(
                        severity=ImportIssueSeverity.ERROR,
                        code="INVALID_SUBMISSION_HEADER",
                        message=str(error),
                    ),
                ),
            )

        issues = self._validate_header(
            header
        )

        return SubmissionBatchItemResult(
            index=index,
            header=header,
            issues=issues,
        )

    @staticmethod
    def _validate_header(
            header: SubmissionHeaderData,
    ) -> tuple[ImportIssue, ...]:
        issues: list[ImportIssue] = []

        if header.supplier_company is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.ERROR,
                    code="SUPPLIER_COMPANY_MISSING",
                    message="supplier company is missing",
                )
            )

        if header.supplier_tax_number is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.ERROR,
                    code="SUPPLIER_TAX_NUMBER_MISSING",
                    message="supplier tax number is missing",
                )
            )

        if header.requester_company is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.ERROR,
                    code="REQUESTER_COMPANY_MISSING",
                    message="requester company is missing",
                )
            )

        if header.requester_tax_number is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.ERROR,
                    code="REQUESTER_TAX_NUMBER_MISSING",
                    message="requester tax number is missing",
                )
            )

        if header.period is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.ERROR,
                    code="SUBMISSION_PERIOD_MISSING",
                    message="submission period is missing",
                )
            )

        if header.respondent_id is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.WARNING,
                    code="RESPONDENT_ID_MISSING",
                    message="respondent id is missing",
                )
            )

        if header.respondent_mp_id is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.WARNING,
                    code="RESPONDENT_MP_ID_MISSING",
                    message="respondent MP id is missing",
                )
            )

        if header.org_size is None:
            issues.append(
                ImportIssue(
                    severity=ImportIssueSeverity.WARNING,
                    code="ORG_SIZE_MISSING",
                    message="organization size is missing",
                )
            )

        return tuple(issues)
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

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("value must be a string or None")

        normalized = value.strip()

        return normalized or None