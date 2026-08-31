from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)
from alex.esg.services.json_import_service import (
    JsonImportService,
)
from alex.esg.services.submission_batch_importer import (
    SubmissionBatchImporter,
)
from alex.esg.services.submission_definition_validator import (
    SubmissionDefinitionValidator,
)


@dataclass(frozen=True)
class SubmissionImportPreview:
    questionnaire: Questionnaire

    question_definitions: tuple[
        QuestionDefinition,
        ...
    ]

    definition_version: str
    submission_version: str

    submission_count: int
    definition_count: int
    response_question_count: int
    matched_question_count: int

    issues: tuple[
        ImportIssue,
        ...
    ]

    @property
    def version_matches(self) -> bool:
        return (
            self.definition_version
            == self.submission_version
        )

    @property
    def errors(
        self,
    ) -> tuple[ImportIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if (
                issue.severity
                is ImportIssueSeverity.ERROR
            )
        )

    @property
    def warnings(
        self,
    ) -> tuple[ImportIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if (
                issue.severity
                is ImportIssueSeverity.WARNING
            )
        )

    @property
    def can_import(self) -> bool:
        return (
            self.version_matches
            and not self.errors
        )


class SubmissionImportPreviewService:
    def __init__(
        self,
        *,
        json_service: JsonImportService,
        definition_mapper: QuestionnaireDefinitionMapper,
        batch_inspector: SubmissionBatchImporter,
        definition_validator: SubmissionDefinitionValidator,
    ) -> None:
        if not isinstance(
            json_service,
            JsonImportService,
        ):
            raise TypeError(
                "json_service must be a JsonImportService"
            )

        if not isinstance(
            definition_mapper,
            QuestionnaireDefinitionMapper,
        ):
            raise TypeError(
                "definition_mapper must be a "
                "QuestionnaireDefinitionMapper"
            )

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

        self._json_service = json_service
        self._definition_mapper = definition_mapper
        self._batch_inspector = batch_inspector
        self._definition_validator = (
            definition_validator
        )

    def preview_files(
        self,
        *,
        definition_file: str | Path,
        submission_file: str | Path,
        questionnaire_code: str,
    ) -> SubmissionImportPreview:
        if not isinstance(
            questionnaire_code,
            str,
        ):
            raise TypeError(
                "questionnaire_code must be a string"
            )

        questionnaire_code = (
            questionnaire_code.strip()
        )

        if not questionnaire_code:
            raise ValueError(
                "questionnaire_code cannot be empty"
            )

        definition_data = (
            self._json_service.load_file(
                definition_file
            )
        )

        submission_data = (
            self._json_service.load_file(
                submission_file
            )
        )

        questionnaire, definitions = (
            self._definition_mapper.map(
                definition_data,
                questionnaire_code=(
                    questionnaire_code
                ),
            )
        )

        inspection = (
            self._batch_inspector.inspect_batch(
                submission_data
            )
        )

        submissions_data = (
            submission_data.get(
                "submissions"
            )
        )

        if not isinstance(
            submissions_data,
            list,
        ):
            raise ValueError(
                "submissions must be a list"
            )

        (
            response_question_count,
            matched_question_count,
        ) = self._count_question_matches(
            submissions_data,
            definitions,
        )

        issues: list[ImportIssue] = []

        if (
            inspection.spec_version
            != questionnaire.spec_version
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
                        "questionnaire definition "
                        f"version "
                        f"{questionnaire.spec_version} "
                        "does not match submission "
                        f"version "
                        f"{inspection.spec_version}"
                    ),
                )
            )

            return SubmissionImportPreview(
                questionnaire=questionnaire,
                question_definitions=definitions,
                definition_version=(
                    questionnaire.spec_version
                ),
                submission_version=(
                    inspection.spec_version
                ),
                submission_count=len(
                    submissions_data
                ),
                definition_count=len(
                    definitions
                ),
                response_question_count=(
                    response_question_count
                ),
                matched_question_count=(
                    matched_question_count
                ),
                issues=tuple(issues),
            )

        for item in inspection.items:
            issues.extend(
                item.issues
            )

        for submission_data_item in (
            submissions_data
        ):
            if not isinstance(
                submission_data_item,
                dict,
            ):
                continue

            response_data = (
                submission_data_item.get(
                    "response"
                )
            )

            if not isinstance(
                response_data,
                dict,
            ):
                continue

            definition_issues = (
                self._definition_validator
                .validate_questions(
                    response_data,
                    question_definitions=(
                        definitions
                    ),
                )
            )

            issues.extend(
                definition_issues
            )

        return SubmissionImportPreview(
            questionnaire=questionnaire,
            question_definitions=definitions,
            definition_version=(
                questionnaire.spec_version
            ),
            submission_version=(
                inspection.spec_version
            ),
            submission_count=len(
                submissions_data
            ),
            definition_count=len(
                definitions
            ),
            response_question_count=(
                response_question_count
            ),
            matched_question_count=(
                matched_question_count
            ),
            issues=tuple(issues),
        )

    @staticmethod
    def _count_question_matches(
        submissions_data: list[Any],
        definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> tuple[int, int]:
        definition_ids = {
            definition.question.question_id
            for definition in definitions
        }

        response_question_count = 0
        matched_question_count = 0

        for submission_data in (
            submissions_data
        ):
            if not isinstance(
                submission_data,
                dict,
            ):
                continue

            response_data = (
                submission_data.get(
                    "response"
                )
            )

            if not isinstance(
                response_data,
                dict,
            ):
                continue

            questions = (
                response_data.get(
                    "questions"
                )
            )

            if not isinstance(
                questions,
                list,
            ):
                continue

            for question_data in questions:
                if not isinstance(
                    question_data,
                    dict,
                ):
                    continue

                response_question_count += 1

                technical_id = (
                    question_data.get(
                        "id"
                    )
                )

                if (
                    isinstance(
                        technical_id,
                        str,
                    )
                    and technical_id
                    in definition_ids
                ):
                    matched_question_count += 1

        return (
            response_question_count,
            matched_question_count,
        )