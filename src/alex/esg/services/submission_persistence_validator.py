from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import (
    SubmissionPersistencePlan,
    SubmissionPersistencePlanner,
)


@dataclass(frozen=True)
class SubmissionPersistenceValidationResult:
    submission_index: int
    relation_id: int
    supplier_tax_number: str
    is_valid: bool
    plan: SubmissionPersistencePlan | None
    error: str | None

    @property
    def answer_count(self) -> int:
        if self.plan is None:
            return 0

        return self.plan.answer_count

    @property
    def answer_value_count(self) -> int:
        if self.plan is None:
            return 0
        return self.plan.answer_value_count

    @property
    def skipped_question_count(self) -> int:
        if self.plan is None:
            return 0

        return len(self.plan.skipped_question_ids)


class SubmissionPersistenceValidator:
    @staticmethod
    def validate(
        *,
        submission_index: int,
        submission_payload: dict,
        batch_id: str,
        relation_id: int,
        supplier_tax_number: str,
        questionnaire_question_ids: set[str],
        option_ids_by_question: dict[
            str,
            set[str],
        ],
    ) -> SubmissionPersistenceValidationResult:
        try:
            plan = (SubmissionPersistencePlanner.create_plan(
                    submission_payload=(submission_payload),
                    batch_id=batch_id,
                    relation_id=relation_id,
                    questionnaire_question_ids=(questionnaire_question_ids),
                    option_ids_by_question=(option_ids_by_question),
                )
            )

        except (
            ValueError,
            TypeError,
        ) as error:
            return (
                SubmissionPersistenceValidationResult(
                    submission_index=(submission_index),
                    relation_id=relation_id,
                    supplier_tax_number=(supplier_tax_number),
                    is_valid=False,
                    plan=None,
                    error=str(error),
                )
            )

        return (
            SubmissionPersistenceValidationResult(
                submission_index=(submission_index),
                relation_id=relation_id,
                supplier_tax_number=(supplier_tax_number),
                is_valid=True,
                plan=plan,
                error=None,
            )
        )