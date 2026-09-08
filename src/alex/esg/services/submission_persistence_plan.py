from dataclasses import dataclass
from alex.esg.services.submission_answer_persistence_mapper import (
    SubmissionAnswerPersistenceData,
    SubmissionAnswerPersistenceMapper,
)
from alex.esg.services.submission_persistence_mapper import (
    SubmissionPersistenceData,
    SubmissionPersistenceMapper,
)


@dataclass(frozen=True)
class SubmissionPersistencePlan:
    submission: SubmissionPersistenceData

    answers: tuple[
        SubmissionAnswerPersistenceData,
        ...
    ]

    skipped_question_ids: tuple[
        str,
        ...
    ]

    @property
    def answer_count(self) -> int:
        return len(self.answers)

    @property
    def answer_value_count(self) -> int:
        return sum(len(answer.values) for answer in self.answers)


class SubmissionPersistencePlanner:
    @staticmethod
    def _required_question_id(
        question_payload: dict,
    ) -> str:
        value = question_payload.get("id")

        if value is None:
            raise ValueError("question id is required")

        question_id = str(value).strip()

        if not question_id:
            raise ValueError("question id cannot be empty")
        return question_id

    @classmethod
    def create_plan(
        cls,
        submission_payload: dict,
        batch_id: str,
        relation_id: int,
        questionnaire_question_ids: set[str],
        option_ids_by_question: dict[
            str,
            set[str],
        ],
        status: str = "imported_complete",
    ) -> SubmissionPersistencePlan:
        if not isinstance(
            submission_payload,
            dict,
        ):
            raise TypeError("submission_payload must be a dict")

        submission_data = (SubmissionPersistenceMapper.map_submission(
                submission_payload=(submission_payload),
                batch_id=batch_id,
                relation_id=relation_id,
                status=status,
            )
        )

        response = (submission_payload.get("response") or {})

        if not isinstance(
            response,
            dict,
        ):
            raise TypeError("response must be a dict")

        questions = (response.get("questions") or [])

        if not isinstance(
            questions,
            list,
        ):
            raise TypeError("questions must be a list")

        answers = []
        skipped_question_ids = []
        seen_question_ids = set()
        for question_payload in questions:
            if not isinstance(
                question_payload,
                dict,
            ):
                raise TypeError("question must be a dict")

            question_id = (cls._required_question_id(question_payload))
            if question_id in seen_question_ids:
                raise ValueError(
                    "duplicate question id "
                    "inside submission: "
                    f"{question_id}"
                )

            seen_question_ids.add(question_id)
            try:
                mapped_answer = (
                    SubmissionAnswerPersistenceMapper
                    .map_question(
                        question_payload=(
                            question_payload
                        ),
                        questionnaire_question_ids=(
                            questionnaire_question_ids
                        ),
                        option_ids_by_question=(
                            option_ids_by_question
                        ),
                    )
                )

            except (
                    ValueError,
                    TypeError,
            ) as error:
                raise ValueError(
                    f"question {question_id}: {error}"
                ) from error

            if mapped_answer is None:
                skipped_question_ids.append(question_id)
                continue

            answers.append(mapped_answer)

        return SubmissionPersistencePlan(
            submission=submission_data,
            answers=tuple(answers),
            skipped_question_ids=tuple(skipped_question_ids),
        )