from dataclasses import dataclass
from pathlib import Path

from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.submission_batch_json_importer import (
    SubmissionBatchJsonImportResult,
    SubmissionBatchJsonImporter,
)
from alex.esg.services.submission_batch_registration_service import SubmissionBatchRegistrationService


@dataclass(frozen=True)
class SubmissionFileImportResult:
    questionnaire: Questionnaire

    question_definitions: tuple[
        QuestionDefinition,
        ...
    ]

    batch_result: SubmissionBatchJsonImportResult

    registered_submissions: tuple[
        Submission,
        ...
    ]

    @property
    def imported_count(self) -> int:
        return len(
            self.registered_submissions
        )

    @property
    def failed_count(self) -> int:
        return self.batch_result.failed_count

    @property
    def is_successful(self) -> bool:
        return self.batch_result.is_successful


class SubmissionFileImportService:
    def __init__(
        self,
        *,
        json_service: JsonImportService,
        definition_mapper: QuestionnaireDefinitionMapper,
        batch_importer: SubmissionBatchJsonImporter,
        registration_service: (
            SubmissionBatchRegistrationService
        ),
    ) -> None:
        if not isinstance(
            json_service,
            JsonImportService,
        ):
            raise TypeError(
                "json_service must be a "
                "JsonImportService"
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
            batch_importer,
            SubmissionBatchJsonImporter,
        ):
            raise TypeError(
                "batch_importer must be a "
                "SubmissionBatchJsonImporter"
            )

        if not isinstance(
            registration_service,
            SubmissionBatchRegistrationService,
        ):
            raise TypeError(
                "registration_service must be a "
                "SubmissionBatchRegistrationService"
            )

        self._json_service = json_service
        self._definition_mapper = (definition_mapper)
        self._batch_importer = batch_importer
        self._registration_service = (registration_service)

    def import_files(
        self,
        *,
        definition_file: str | Path,
        submission_file: str | Path,
        questionnaire_code: str,
    ) -> SubmissionFileImportResult:
        if not isinstance(
            questionnaire_code,
            str,
        ):
            raise TypeError("questionnaire_code must be a string")

        questionnaire_code = (questionnaire_code.strip())

        if not questionnaire_code:
            raise ValueError("questionnaire_code cannot be empty")

        definition_data = (self._json_service.load_file(definition_file))

        submission_data = (self._json_service.load_file(submission_file))

        questionnaire, definitions = (
            self._definition_mapper.map(
                definition_data,
                questionnaire_code=(
                    questionnaire_code
                ),
            )
        )

        batch_result = (
            self._batch_importer.import_batch(
                submission_data,
                questionnaire=questionnaire,
                question_definitions=definitions,
            )
        )

        registered = (self._registration_service.register_import_result( batch_result))

        return SubmissionFileImportResult(
            questionnaire=questionnaire,
            question_definitions=definitions,
            batch_result=batch_result,
            registered_submissions=registered,
        )