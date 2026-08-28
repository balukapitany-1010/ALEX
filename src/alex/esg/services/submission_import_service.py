from typing import Any

from alex.esg.domain.answer import Answer
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.submission import Submission
from alex.esg.mappers.submission_answer_mapper import (
    SubmissionAnswerMapper,
)


class SubmissionImportService:
    def __init__(
        self,
        answer_mapper: SubmissionAnswerMapper | None = None,
    ) -> None:
        self._answer_mapper = (
            answer_mapper
            if answer_mapper is not None
            else SubmissionAnswerMapper()
        )

    def import_answers(
        self,
        response_data: dict[str, Any],
        *,
        submission: Submission,
        question_definitions: tuple[QuestionDefinition, ...],
    ) -> tuple[Answer, ...]:
        if not isinstance(response_data, dict):
            raise TypeError("response_data must be a dictionary")

        if not isinstance(submission, Submission):
            raise TypeError("submission must be a Submission")

        if not isinstance(
            question_definitions,
            tuple,
        ):
            raise TypeError("question_definitions must be a tuple")

        answers = self._answer_mapper.map_answers(
            response_data,
            submission=submission,
            question_definitions=question_definitions,
        )

        for answer in answers:
            submission.add_answer(answer)

        return answers

    def validate_spec_version(
            self,
            batch_data: dict[str, Any],
            *,
            submission: Submission,
    ) -> None:
        if not isinstance(batch_data, dict):
            raise TypeError("batch_data must be a dictionary")

        spec_version = batch_data.get("spec_version")

        if not isinstance(spec_version, str):
            raise ValueError("spec_version is required")

        spec_version = spec_version.strip()

        if (
                submission.questionnaire.spec_version
                != spec_version
        ):
            raise ValueError(
                "submission questionnaire version "
                f"{submission.questionnaire.spec_version} "
                "does not match JSON spec_version "
                f"{spec_version}"
            )