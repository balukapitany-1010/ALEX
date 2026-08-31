from typing import Any

from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderMapper
from alex.esg.services.submission_builder_service import SubmissionBuilderService
from alex.esg.services.submission_import_service import SubmissionImportService


class SubmissionJsonImporter:
    def __init__(
        self,
        *,
        header_mapper: SubmissionHeaderMapper,
        builder: SubmissionBuilderService,
        submission_import_service: SubmissionImportService,
    ) -> None:
        if not isinstance(
            header_mapper,
            SubmissionHeaderMapper,
        ):
            raise TypeError(
                "header_mapper must be a "
                "SubmissionHeaderMapper"
            )

        if not isinstance(
            builder,
            SubmissionBuilderService,
        ):
            raise TypeError(
                "builder must be a "
                "SubmissionBuilderService"
            )

        if not isinstance(
            submission_import_service,
            SubmissionImportService,
        ):
            raise TypeError(
                "submission_import_service must be a "
                "SubmissionImportService"
            )

        self._header_mapper = header_mapper
        self._builder = builder
        self._submission_import_service = (
            submission_import_service
        )

    def import_submission(
        self,
        submission_data: dict[str, Any],
        *,
        spec_version: str,
        questionnaire: Questionnaire,
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> Submission:
        if not isinstance(
            submission_data,
            dict,
        ):
            raise TypeError("submission_data must be a dictionary")

        if not isinstance(
            spec_version,
            str,
        ):
            raise TypeError("spec_version must be a string")

        spec_version = spec_version.strip()

        if not spec_version:
            raise ValueError("spec_version cannot be empty")

        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError(
                "questionnaire must be a Questionnaire"
            )

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

        if (
            spec_version
            != questionnaire.spec_version
        ):
            raise ValueError(
                "questionnaire version "
                f"{questionnaire.spec_version} "
                "does not match submission "
                f"version {spec_version}"
            )

        response_data = submission_data.get("response")

        if not isinstance(
            response_data,
            dict,
        ):
            raise ValueError("submission response must be an object")

        header = self._header_mapper.map(submission_data)

        submission = self._builder.build(
            header=header,
            questionnaire=questionnaire,
        )

        self._submission_import_service.import_answers(
            response_data,
            submission=submission,
            question_definitions=(question_definitions
            ),
        )

        return submission