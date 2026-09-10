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
    batch_exists: bool
    spec_version: str
    items: tuple[
        SubmissionImportItemResult,
        ...
    ]

    @property
    def batch_is_new(self) -> bool:
        return not self.batch_exists
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
    batch_created: bool
    write_results: tuple

    verification_result: object | None = None
    verification_error: str | None = None

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

    @property
    def verification_succeeded(self) -> bool | None:
        if not self.batch_created:
            return None

        if self.verification_error is not None:
            return False

        if self.verification_result is None:
            return False

        return self.verification_result.is_valid
class SubmissionImportOrchestrator:
    def __init__(
            self,
            *,
            context_reader,
            submission_writer,
            import_writer=None,
            import_verifier=None,
    ) -> None:
        self._context_reader = (context_reader)
        self._submission_writer = (submission_writer)
        self._import_writer = (import_writer)
        self._import_verifier = (import_verifier)

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

    @staticmethod
    def _normalize_respondent_id_for_key(
            value,
    ) -> str:
        if value is None:
            return ""

        text = str(
            value
        ).strip().upper()

        if not text:
            return ""

        if not text.startswith(
                "RESP_"
        ):
            return text

        body = text[5:]

        identifier, separator, period = (
            body.rpartition("_")
        )

        if not separator:
            return text

        normalized_identifier = "".join(
            character
            for character in identifier
            if character.isalnum()
        )

        normalized_period = "".join(
            character
            for character in period
            if character.isalnum()
        )

        return (
            f"RESP_{normalized_identifier}_"
            f"{normalized_period}"
        )

    @classmethod
    def _submission_natural_key(
            cls,
            plan: SubmissionPersistencePlan,
    ) -> tuple:
        submission = plan.submission

        respondent_mp_id = (
            None
            if submission.respondent_mp_id is None
            else str(
                submission.respondent_mp_id
            ).strip()
        )

        return (
            submission.batch_id,
            submission.relation_id,
            cls._normalize_respondent_id_for_key(
                submission.respondent_id
            ),
            respondent_mp_id,
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
        context = (
            self._context_reader.load_context(
                batch_id=batch_id,
                questionnaire_code=(questionnaire_code),
                spec_version=(spec_version),
                allow_missing_batch=True,
            )
        )
        results = []

        results = []

        seen_natural_keys = {}

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
                natural_key = (
                    self._submission_natural_key(
                        plan
                    )
                )

                first_occurrence = (
                    seen_natural_keys.get(
                        natural_key
                    )
                )

                if first_occurrence is not None:
                    results.append(
                        SubmissionImportItemResult(
                            submission_index=index,
                            supplier_tax_number=(
                                supplier_tax_number
                            ),
                            requester_tax_number=(
                                requester_tax_number
                            ),
                            relation_id=relation_id,
                            plan=None,
                            existing_submission_id=None,
                            is_new=False,
                            error=(
                                "duplicate submission in import; "
                                "first occurrence: "
                                f"{first_occurrence}"
                            ),
                        )
                    )

                    continue

                seen_natural_keys[
                    natural_key
                ] = index

                if context.batch_exists:
                    preflight = (self._submission_writer.preflight(plan))
                    existing_submission_id = (preflight.existing_submission_id)
                    is_new = preflight.can_insert

                else:
                    existing_submission_id = None
                    is_new = True

                results.append(SubmissionImportItemResult(
                        submission_index=index,
                        supplier_tax_number=(supplier_tax_number),
                        requester_tax_number=(requester_tax_number),
                        relation_id=relation_id,
                        plan=plan,
                        existing_submission_id=(existing_submission_id),
                        is_new=is_new,
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

        return (SubmissionImportDryRunResult(
                batch_id=batch_id,
                questionnaire_code=(questionnaire_code),
                batch_exists=(context.batch_exists),
                spec_version=spec_version,
                items=tuple(results),
            )
        )

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

        plans = [item.plan for item in dry_run.items if item.plan is not None]
        if len(plans) != dry_run.submission_count:
            raise RuntimeError("not every submission has a persistence plan")
        if self._import_writer is None:
            raise RuntimeError("import_writer is required for execute")

        import_result = (self._import_writer.write(
                batch_id=dry_run.batch_id,
                questionnaire_code=(dry_run.questionnaire_code),
                spec_version=(dry_run.spec_version),
                plans=plans,
            )
        )

        verification_result = None
        verification_error = None

        if import_result.batch_created:
            if self._import_verifier is None:
                verification_error = ("import_verifier is not configured")

            else:
                try:
                    verification_result = (self._import_verifier.verify_new_batch(
                            batch_id=(dry_run.batch_id),
                            questionnaire_code=(dry_run.questionnaire_code),
                            spec_version=(dry_run.spec_version),
                            plans=plans,
                        )
                    )

                except Exception as error:
                    verification_error = str(error)

        return SubmissionImportExecutionResult(
            dry_run=dry_run,
            batch_created=(import_result.batch_created),
            write_results=(import_result.submission_results),
            verification_result=(verification_result),
            verification_error=(verification_error),
        )

    def execute_rollback(
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

        if self._import_writer is None:
            raise RuntimeError(
                "import_writer is required "
                "for execute"
            )

        import_result = (
            self._import_writer.write_rollback(
                batch_id=dry_run.batch_id,
                questionnaire_code=(
                    dry_run.questionnaire_code
                ),
                spec_version=(
                    dry_run.spec_version
                ),
                plans=plans,
            )
        )

        return SubmissionImportExecutionResult(
            dry_run=dry_run,
            batch_created=(
                import_result.batch_created
            ),
            write_results=(
                import_result.submission_results
            ),
        )

