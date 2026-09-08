from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import (
    SubmissionPersistencePlan,
    SubmissionPersistencePlanner,
)


@dataclass(frozen=True)
class SubmissionImportItemResult:
    submission_index: int
    supplier_tax_number: str | None
    requester_tax_number: str | None
    relation_id: int | None
    plan: SubmissionPersistencePlan | None
    existing_submission_id: int | None
    is_new: bool
    error: str | None

    @property
    def is_valid(self) -> bool:
        return self.error is None

    @property
    def exists(self) -> bool:
        return (self.existing_submission_id is not None)

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


@dataclass(frozen=True)
class SubmissionImportDryRunResult:
    batch_id: str
    questionnaire_code: str
    spec_version: str
    items: tuple[
        SubmissionImportItemResult,
        ...
    ]

    @property
    def submission_count(self) -> int:
        return len(self.items)

    @property
    def existing_count(self) -> int:
        return sum(1 for item in self.items if (item.is_valid and item.exists))

    @property
    def new_count(self) -> int:
        return sum(1 for item in self.items if (item.is_valid and item.is_new))

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.items if not item.is_valid)

    @property
    def answer_count(self) -> int:
        return sum(item.answer_count for item in self.items if item.is_valid)

    @property
    def answer_value_count(self) -> int:
        return sum(item.answer_value_count for item in self.items if item.is_valid)

@dataclass(frozen=True)
class SubmissionImportExecutionResult:
    dry_run: SubmissionImportDryRunResult
    write_results: tuple

    @property
    def created_count(self) -> int:
        return sum(1 for result in self.write_results if result.created)

    @property
    def existing_count(self) -> int:
        return sum(1 for result in self.write_results if not result.created)

    @property
    def created_answer_count(self) -> int:
        return sum(result.answer_count for result in self.write_results if result.created)

    @property
    def created_answer_value_count(self) -> int:
        return sum(result.answer_value_count for result in self.write_results if result.created)

class SubmissionImportOrchestrator:
    def __init__(
        self,
        *,
        context_reader,
        submission_writer,
    ) -> None:
        self._context_reader = (context_reader)
        self._submission_writer = (submission_writer)

    @staticmethod
    def _optional_text(
        value,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    @classmethod
    def _get_tax_numbers(
        cls,
        submission_payload: dict,
    ) -> tuple[
        str | None,
        str | None,
    ]:
        response = (submission_payload.get("response")or {})
        cover = (response.get("cover")or {})
        supplier = (cover.get("supplier") or {})
        requester = (cover.get("requester") or {})
        supplier_tax_number = (cls._optional_text(supplier.get("tax_number")))
        requester_tax_number = (cls._optional_text(requester.get("tax_number")))
        return (
            supplier_tax_number,
            requester_tax_number,
        )

    @classmethod
    def dry_run(
        cls,
        *,
        payload: dict,
        batch_id: str,
        context_reader,
        submission_writer,
    ) -> SubmissionImportDryRunResult:
        orchestrator = cls(
            context_reader=context_reader,
            submission_writer=(submission_writer),
        )

        return orchestrator.run_dry_run(
            payload=payload,
            batch_id=batch_id,
        )

    def run_dry_run(
        self,
        *,
        payload: dict,
        batch_id: str,
    ) -> SubmissionImportDryRunResult:
        if not isinstance(
            payload,
            dict,
        ):
            raise TypeError("payload must be a dict")
        batch_id = self._optional_text(batch_id)

        if batch_id is None:
            raise ValueError("batch_id cannot be empty")
        spec_version = (self._optional_text(payload.get("spec_version")))
        if spec_version is None:
            raise ValueError(
                "spec_version is required"
            )
        submissions = payload.get("submissions")
        if (
            not isinstance(
                submissions,
                list,
            ) or not submissions
        ):
            raise ValueError("submissions must be a non-empty list")
        first_submission = (submissions[0])
        if not isinstance(
            first_submission,
            dict,
        ):
            raise ValueError("first submission must be a dict")

        first_response = (first_submission.get("response")or {})

        questionnaire_code = (self._optional_text(first_response.get("survey_type")) or "SZTFH")
        context = (self._context_reader.load_context(
                batch_id=batch_id,
                questionnaire_code=(questionnaire_code),
                spec_version=(spec_version),
            )
        )
        results = []

        for index, submission in enumerate(
            submissions,
            start=1,
        ):
            if not isinstance(
                submission,
                dict,
            ):
                results.append(
                    SubmissionImportItemResult(
                        submission_index=index,
                        supplier_tax_number=None,
                        requester_tax_number=None,
                        relation_id=None,
                        plan=None,
                        existing_submission_id=None,
                        is_new=False,
                        error=("submission must be a dict"),
                    )
                )
                continue
            (
                supplier_tax_number,
                requester_tax_number,
            ) = self._get_tax_numbers( submission)

            try:
                if supplier_tax_number is None:
                    raise ValueError("supplier tax_number is required")
                if requester_tax_number is None:
                    raise ValueError("requester tax_number is required")
                response = (submission.get("response") or {})
                current_questionnaire_code = (self._optional_text(response.get("survey_type"))or questionnaire_code)
                if (current_questionnaire_code != questionnaire_code):
                    raise ValueError("submission survey_type does not match batch")

                relation_id = (self._context_reader.resolve_relation_id(
                        requester_tax_number=(requester_tax_number),
                        supplier_tax_number=(supplier_tax_number),
                    )
                )

                plan = (
                    SubmissionPersistencePlanner.create_plan(
                        submission_payload=(submission),
                        batch_id=batch_id,
                        relation_id=relation_id,
                        questionnaire_question_ids=(set(context.questionnaire_question_ids)),
                        option_ids_by_question={question_id: set(option_ids)
                            for (question_id, option_ids,) in (context.option_ids_by_question.items())},
                    )
                )

                preflight = (self._submission_writer.preflight(plan))

                results.append(SubmissionImportItemResult(
                        submission_index=index,
                        supplier_tax_number=(supplier_tax_number),
                        requester_tax_number=(requester_tax_number),
                        relation_id=relation_id,
                        plan=plan,
                        existing_submission_id=(preflight.existing_submission_id),
                        is_new=(preflight.can_insert),
                        error=None,
                    )
                )

            except Exception as error:
                results.append(SubmissionImportItemResult(
                        submission_index=index,
                        supplier_tax_number=(supplier_tax_number),
                        requester_tax_number=(requester_tax_number),
                        relation_id=None,
                        plan=None,
                        existing_submission_id=None,
                        is_new=False,
                        error=str(error),
                    )
                )

        return (
            SubmissionImportDryRunResult(
                batch_id=batch_id,
                questionnaire_code=(questionnaire_code),
                spec_version=spec_version,
                items=tuple(results),))

    def execute(
            self,
            *,
            payload: dict,
            batch_id: str,
    ) -> SubmissionImportExecutionResult:
        dry_run = self.run_dry_run(
            payload=payload,
            batch_id=batch_id,
        )

        if dry_run.error_count:
            raise ValueError(
                "submission import contains "
                f"{dry_run.error_count} error(s); "
                "database write aborted"
            )

        plans = [
            item.plan
            for item in dry_run.items
            if item.plan is not None
        ]

        if len(plans) != dry_run.submission_count:
            raise RuntimeError(
                "not every submission has "
                "a persistence plan"
            )

        write_results = (
            self._submission_writer
            .write_many(
                plans
            )
        )

        return SubmissionImportExecutionResult(
            dry_run=dry_run,
            write_results=write_results,
        )

