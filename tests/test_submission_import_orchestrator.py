from dataclasses import dataclass
from alex.esg.services.submission_import_orchestrator import (
    SubmissionImportDryRunResult,
    SubmissionImportItemResult,
    SubmissionImportOrchestrator,
)
from copy import deepcopy
import pytest
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceData

@dataclass(frozen=True)
class FakeSupplementWriteResult:
    supplement_submission_count: int
    answer_count: int
    answer_value_count: int


@dataclass(frozen=True)
class FakeSupplementVerificationResult:
    is_valid: bool

@dataclass(frozen=True)
class FakeVerificationResult:
    is_valid: bool

class FakeImportVerifier:
    def __init__(
        self,
        *,
        is_valid=True,
        fail=False,
        supplement_is_valid=True,
        supplement_fail=False,
        written_is_valid=True,
        written_fail=False,
    ):
        self.written_is_valid = (written_is_valid)
        self.written_fail = (written_fail)
        self.verify_written_results_calls = 0
        self.last_written_plans = None
        self.last_written_results = None
        self.supplement_is_valid = (supplement_is_valid)
        self.supplement_fail = (supplement_fail)
        self.verify_supplement_items_calls = 0
        self.last_supplement_items = None
        self.is_valid = is_valid
        self.fail = fail
        self.verify_calls = 0
        self.last_batch_id = None
        self.last_questionnaire_code = None
        self.last_spec_version = None
        self.last_plans = None

    def verify_written_results(
        self,
        *,
        plans,
        write_results,
    ):
        self.verify_written_results_calls += 1
        self.last_written_plans = list(plans)
        self.last_written_results = tuple(write_results)
        if self.written_fail:
            raise RuntimeError("written verification failed")
        return FakeVerificationResult(is_valid=self.written_is_valid)

    def verify_supplement_items(
        self,
        *,
        items,
    ):
        self.verify_supplement_items_calls += 1
        self.last_supplement_items = list(items)
        if self.supplement_fail:
            raise RuntimeError("supplement verification failed")
        return FakeSupplementVerificationResult(is_valid=(self.supplement_is_valid))

    def verify_new_batch(
        self,
        *,
        batch_id,
        questionnaire_code,
        spec_version,
        plans,
    ):
        self.verify_calls += 1
        self.last_batch_id = batch_id
        self.last_questionnaire_code = (
            questionnaire_code
        )
        self.last_spec_version = (
            spec_version
        )
        self.last_plans = plans

        if self.fail:
            raise RuntimeError(
                "verification failed"
            )

        return FakeVerificationResult(
            is_valid=self.is_valid
        )
@dataclass(frozen=True)
class FakeContext:
    questionnaire_code: str
    spec_version: str
    batch_exists: bool
    batch_id: str
    questionnaire_question_ids: frozenset[str]
    option_ids_by_question: dict[
        str,
        frozenset[str],
    ]


@dataclass(frozen=True)
class FakePreflightResult:
    existing_submission_id: int | None

    @property
    def can_insert(self) -> bool:
        return (self.existing_submission_id is None)

@dataclass(frozen=True)
class FakeSupplementPreflightResult:
    existing_submission_id: int | None
    supplement_answers: tuple

    @property
    def is_supplement(self) -> bool:
        return (
            self.existing_submission_id
            is not None
            and bool(
                self.supplement_answers
            )
        )

class FakeContextReader:
    def __init__(
            self,
            relation_id=274,
            relation_ids_by_supplier_tax=None,
            batch_exists=True,
    ):
        self.relation_id = relation_id
        self.relation_ids_by_supplier_tax = (relation_ids_by_supplier_tax)
        self.batch_exists = batch_exists

    def load_context(
            self,
            *,
            batch_id,
            questionnaire_code,
            spec_version,
            allow_missing_batch=False,
    ):
        return FakeContext(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version,
            batch_id=batch_id,
            batch_exists=self.batch_exists,
            questionnaire_question_ids=(
                frozenset(
                    {
                        "TEST_Q",
                    }
                )
            ),
            option_ids_by_question={
                "TEST_Q": frozenset(
                    {
                        "TEST_Q_1",
                    }
                )
            },
        )

    def resolve_relation_id(
            self,
            *,
            requester_tax_number,
            supplier_tax_number,
    ):
        if (
                self.relation_ids_by_supplier_tax is not None
        ):
            return (self.relation_ids_by_supplier_tax[supplier_tax_number])

        return self.relation_id
@dataclass(frozen=True)
class FakeImportWriteResult:
    batch_created: bool
    submission_results: tuple


class FakeImportWriter:
    def __init__(
        self,
        *,
        batch_created=False,
        submission_results=(),
        supplement_result=None,
        supplement_fail=False,

    ):
        self.batch_created = (batch_created)
        self.submission_results = tuple(submission_results)
        self.write_calls = 0
        self.last_batch_id = None
        self.last_questionnaire_code = None
        self.last_spec_version = None
        self.last_plans = None
        self.write_rollback_calls = 0
        self.supplement_result = (supplement_result)
        self.supplement_fail = (supplement_fail)
        self.write_supplement_items_calls = 0
        self.last_supplement_items = None

    def write_supplement_items(
        self,
        *,
        items,
    ):
        self.write_supplement_items_calls += 1
        self.last_supplement_items = list(items)
        if self.supplement_fail:
            raise RuntimeError("supplement write failed")
        return self.supplement_result

    def write(
        self,
        *,
        batch_id,
        questionnaire_code,
        spec_version,
        plans,
    ):
        self.write_calls += 1
        self.last_batch_id = (batch_id)
        self.last_questionnaire_code = (questionnaire_code)
        self.last_spec_version = (spec_version)
        self.last_plans = (plans)
        return FakeImportWriteResult(
            batch_created=(self.batch_created),
            submission_results=(self.submission_results),
        )

    def write_rollback(
            self,
            *,
            batch_id,
            questionnaire_code,
            spec_version,
            plans,
    ):
        self.write_rollback_calls += 1
        self.last_batch_id = (batch_id)
        self.last_questionnaire_code = (questionnaire_code)
        self.last_spec_version = (spec_version)
        self.last_plans = (plans)

        return FakeImportWriteResult(
            batch_created=(self.batch_created),
            submission_results=(self.submission_results),
        )

@dataclass(frozen=True)
class FakeWriteResult:
    submission_id: int
    created: bool
    answer_count: int
    answer_value_count: int
class FakeWriter:
    def __init__(
            self,
            existing_submission_id=323,
            existing_submission_ids_by_relation=None,
            supplement_existing_submission_id=None,
            supplement_has_answers=False,

    ):
        self.existing_submission_id = (existing_submission_id)
        self.existing_submission_ids_by_relation = (existing_submission_ids_by_relation)
        self.preflight_calls = 0
        self.write_many_calls = 0
        self.write_many_plans = None
        self.supplement_existing_submission_id = (supplement_existing_submission_id)
        self.supplement_has_answers = (supplement_has_answers)
        self.preflight_supplement_calls = 0


    def preflight_supplement(
            self,
            plan,
    ):
        self.preflight_supplement_calls += 1

        supplement_answers = (
            plan.answers
            if self.supplement_has_answers
            else ()
        )

        return FakeSupplementPreflightResult(
            existing_submission_id=(
                self.supplement_existing_submission_id
            ),
            supplement_answers=(
                supplement_answers
            ),
        )

    def _get_existing_submission_id(
            self,
            plan,
    ):
        if (
                self.existing_submission_ids_by_relation is not None
        ):
            return (self.existing_submission_ids_by_relation.get(plan.submission.relation_id))
        return self.existing_submission_id

    def preflight(
            self,
            plan,
    ):
        self.preflight_calls += 1
        return FakePreflightResult(existing_submission_id=(self._get_existing_submission_id( plan)))

    def write_many(
            self,
            plans,
    ):
        self.write_many_calls += 1
        self.write_many_plans = plans
        results = []
        for index, plan in enumerate(
                plans,
                start=1,
        ):
            existing_submission_id = (self._get_existing_submission_id(plan ))
            if existing_submission_id is not None:
                results.append(FakeWriteResult(
                        submission_id=(existing_submission_id),
                        created=False,
                        answer_count=0,
                        answer_value_count=0,
                    )
                )
                continue
            results.append(FakeWriteResult(
                    submission_id=(1000 + index),
                    created=True,
                    answer_count=(plan.answer_count),
                    answer_value_count=(plan.answer_value_count),
                )
            )
        return tuple(
            results
        )
def create_payload():
    return {
        "spec_version": "2.0",
        "submissions": [
            {
                "supplier_key": None,
                "response": {
                    "survey_type": "SZTFH",
                    "respondent_id": None,
                    "respondent_MP_id": None,
                    "org_size": None,
                    "submitted_at": (
                        "2026-02-26T07:39:59Z"
                    ),
                    "cover": {
                        "supplier": {
                            "tax_number": (
                                "11102481207"
                            ),
                            "period": "2024",
                        },
                        "requester": {
                            "tax_number": (
                                "11107792-2-44"
                            ),
                        },
                    },
                    "questions": [
                        {
                            "id": "TEST_Q",
                            "fields": [
                                {
                                    "type": (
                                        "number"
                                    ),
                                    "values": [
                                        {
                                            "optionId": (
                                                "TEST_Q_1"
                                            ),
                                            "value": (
                                                "14.20838"
                                            ),
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
            }
        ],
    }
def create_mixed_payload():
    payload = create_payload()
    second_submission = deepcopy(payload["submissions"][0])
    second_submission[
        "response"
    ][
        "cover"
    ][
        "supplier"
    ][
        "tax_number"
    ] = "10654411243"

    second_submission[
        "response"
    ][
        "cover"
    ][
        "supplier"
    ]["period"] = "2024"

    payload["submissions"].append(second_submission)
    return payload


def test_dry_run_reports_existing_submission():
    writer = FakeWriter(existing_submission_id=323)
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(),
        submission_writer=writer,
    )
    result = (orchestrator.run_dry_run(
            payload=create_payload(),
            batch_id="BATCH_TEST",
        )
    )

    assert result.submission_count == 1
    assert result.existing_count == 1
    assert result.new_count == 0
    assert result.error_count == 0
    assert result.answer_count == 1
    assert result.answer_value_count == 1
    assert (result.items[0].existing_submission_id == 323)
    assert writer.preflight_calls == 1


def test_dry_run_reports_new_submission():
    writer = FakeWriter(
        existing_submission_id=None
    )

    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(),
        submission_writer=writer,
    )

    result = (orchestrator.run_dry_run(
            payload=create_payload(),
            batch_id="BATCH_TEST",
        )
    )
    assert result.existing_count == 0
    assert result.new_count == 1
    assert result.error_count == 0


def test_dry_run_collects_submission_error():
    payload = create_payload()
    payload[
        "submissions"
    ][0][
        "response"
    ][
        "cover"
    ][
        "supplier"
    ][
        "tax_number"
    ] = None

    writer = FakeWriter()
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(),
        submission_writer=writer,
    )

    result = (orchestrator.run_dry_run(
            payload=payload,
            batch_id="BATCH_TEST",
        )
    )
    assert result.submission_count == 1
    assert result.error_count == 1
    assert result.existing_count == 0
    assert result.new_count == 0
    assert ("supplier tax_number is required" in result.items[0].error)
    assert writer.preflight_calls == 0

def test_execute_writes_valid_plans():
    writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=False,
        submission_results=(
            FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
            import_writer=import_writer,
        )
    )
    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert import_writer.write_calls == 1
    assert len(import_writer.last_plans) == 1
    assert result.created_count == 1
    assert result.existing_count == 0
    assert result.created_answer_count == 1
    assert result.created_answer_value_count == 1


def test_execute_aborts_before_write_when_dry_run_has_error():
    payload = create_payload()

    payload[
        "submissions"
    ][0][
        "response"
    ][
        "cover"
    ][
        "supplier"
    ][
        "tax_number"
    ] = None

    writer = FakeWriter()
    import_writer = FakeImportWriter()
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
            import_writer=import_writer,
        )
    )
    import pytest
    with pytest.raises(
        ValueError,
        match="database write aborted",
    ):
        orchestrator.execute(
            payload=payload,
            batch_id="BATCH_TEST",
        )
    assert import_writer.write_calls == 0

def test_execute_reports_existing_submission():

    writer = FakeWriter(existing_submission_id=323)
    import_writer = FakeImportWriter(
        batch_created=False,
        submission_results=(
            FakeWriteResult(
                submission_id=323,
                created=False,
                answer_count=0,
                answer_value_count=0,
            ),
        ),
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
            import_writer=import_writer,
        )
    )
    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert import_writer.write_calls == 1
    assert result.created_count == 0
    assert result.existing_count == 1
    assert (result.created_answer_count == 0)
    assert (result.created_answer_value_count == 0)
    assert result.batch_created is False
    assert result.write_results[0].submission_id == 323
    assert result.write_results[0].created is False

def test_execute_handles_existing_and_new_submissions():
    import_verifier = FakeImportVerifier(written_is_valid=True)
    payload = create_mixed_payload()
    context_reader = FakeContextReader(
        relation_ids_by_supplier_tax={
            "11102481207": 274,
            "10654411243": 275,
        }
    )
    writer = FakeWriter(
        existing_submission_ids_by_relation={
            274: 323,
            275: None,
        }
    )
    import_writer = FakeImportWriter(
        batch_created=False,
        submission_results=(
            FakeWriteResult(
                submission_id=323,
                created=False,
                answer_count=0,
                answer_value_count=0,
            ),
            FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    orchestrator = SubmissionImportOrchestrator(
        context_reader=context_reader,
        submission_writer=writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )
    result = orchestrator.execute(
        payload=payload,
        batch_id="BATCH_TEST",
    )

    assert result.dry_run.submission_count == 2
    assert result.dry_run.existing_count == 1
    assert result.dry_run.new_count == 1
    assert result.dry_run.error_count == 0
    assert import_writer.write_calls == 1
    assert len(import_writer.last_plans) == 2
    assert result.created_count == 1
    assert result.existing_count == 1
    assert result.created_answer_count == 1
    assert result.created_answer_value_count == 1
    assert (result.write_results[0].submission_id == 323)
    assert (result.write_results[0].created is False)
    assert (result.write_results[1].created is True)
    assert (import_verifier.verify_written_results_calls == 1)
    assert (result.verification_succeeded is True)

def test_dry_run_supports_new_batch_without_preflight():
    writer = FakeWriter(
        existing_submission_id=None
    )
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=False),
        submission_writer=writer,
    )
    result = orchestrator.run_dry_run(
        payload=create_payload(),
        batch_id="NEW_BATCH",
    )

    assert result.batch_exists is False
    assert result.batch_is_new is True
    assert result.submission_count == 1
    assert result.new_count == 1
    assert result.existing_count == 0
    assert result.error_count == 0
    assert writer.preflight_calls == 0


def test_execute_supports_new_batch_atomically():
    submission_writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=True,
        submission_results=(
            FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader(batch_exists=False)),
            submission_writer=(submission_writer),
            import_writer=(import_writer),
        )
    )
    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="NEW_BATCH",
    )
    assert (result.batch_created is True)
    assert result.created_count == 1
    assert result.existing_count == 0
    assert import_writer.write_calls == 1
    assert (import_writer.last_batch_id == "NEW_BATCH")
    assert (import_writer.last_questionnaire_code == "SZTFH")
    assert (import_writer.last_spec_version == "2.0")

def test_execute_requires_import_writer():
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader(batch_exists=True)),
            submission_writer=(FakeWriter(existing_submission_id=323)),
        )
    )
    with pytest.raises(
        RuntimeError,
        match="import_writer is required",
    ):
        orchestrator.execute(
            payload=create_payload(),
            batch_id="BATCH_TEST",
        )
def test_execute_rollback_uses_rollback_writer():
    submission_writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=True,
        submission_results=(FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=False),
        submission_writer=(submission_writer),
        import_writer=import_writer,
    )
    result = orchestrator.execute_rollback(
        payload=create_payload(),
        batch_id="NEW_BATCH",
    )
    assert result.batch_created is True
    assert result.created_count == 1
    assert (import_writer.write_rollback_calls == 1)
    assert import_writer.write_calls == 0
    assert (import_writer.last_batch_id == "NEW_BATCH")

def test_execute_reports_failed_post_write_verification():
    submission_writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=True,
        submission_results=(FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    import_verifier = FakeImportVerifier(is_valid=False)
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=False),
        submission_writer=submission_writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )
    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="NEW_BATCH",
    )

    assert result.batch_created is True
    assert result.created_count == 1
    assert result.existing_count == 0
    assert (import_verifier.verify_calls == 1)
    assert (result.verification_result is not None)
    assert (result.verification_result.is_valid is False)
    assert (result.verification_error is None)
    assert (result.verification_succeeded is False)

def test_execute_preserves_commit_when_verifier_fails():
    submission_writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=True,
        submission_results=(FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )
    import_verifier = FakeImportVerifier(fail=True)
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=False),
        submission_writer=submission_writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )
    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="NEW_BATCH",
    )
    assert result.batch_created is True
    assert result.created_count == 1
    assert (import_verifier.verify_calls == 1)
    assert (result.verification_result is None)
    assert (result.verification_error == "verification failed")
    assert (result.verification_succeeded is False)

def test_dry_run_rejects_duplicate_submission_in_same_import():
    payload = create_payload()
    duplicate = deepcopy(payload["submissions"][0])
    payload["submissions"].append(duplicate)
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=(FakeWriter(existing_submission_id=323)),
        )
    )
    result = orchestrator.run_dry_run(
        payload=payload,
        batch_id="BATCH_TEST",
    )

    assert result.submission_count == 2
    assert result.existing_count == 1
    assert result.new_count == 0
    assert result.error_count == 1
    assert result.items[0].is_valid is True
    assert result.items[1].is_valid is False
    assert (result.items[1].error == ("duplicate submission in import; first occurrence: 1"))

def test_dry_run_accepts_distinct_submissions_in_same_import():
    payload = create_payload()
    second = deepcopy(payload["submissions"][0])
    second[
        "response"
    ][
        "cover"
    ][
        "supplier"
    ][
        "tax_number"
    ] = "87654321"

    payload["submissions"].append(second)
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=(FakeWriter(existing_submission_id=None)),
        )
    )
    result = orchestrator.run_dry_run(
        payload=payload,
        batch_id="BATCH_TEST",
    )

    assert result.submission_count == 2
    assert result.error_count == 0

def test_item_reports_supplement_counts():
    plan = create_payload()
    answer = SubmissionAnswerPersistenceData(
        question_id="DETAIL_TEST",
        values=(),
    )
    item = SubmissionImportItemResult(
        submission_index=1,
        supplier_tax_number="11102481-2-07",
        requester_tax_number="12345678",
        relation_id=274,
        plan=None,
        existing_submission_id=323,
        is_new=False,
        error=None,
        supplement_answers=(answer,),
    )

    assert item.is_supplement is True
    assert item.exists is True
    assert item.supplement_answer_count == 1
    assert (item.supplement_answer_value_count == 0)

def test_dry_run_counts_supplement_separately():
    answer = SubmissionAnswerPersistenceData(
        question_id="DETAIL_TEST",
        values=(),
    )
    item = SubmissionImportItemResult(
        submission_index=1,
        supplier_tax_number="11102481-2-07",
        requester_tax_number="12345678",
        relation_id=274,
        plan=None,
        existing_submission_id=323,
        is_new=False,
        error=None,
        supplement_answers=(answer,),
    )
    result = SubmissionImportDryRunResult(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        batch_exists=True,
        spec_version="2.0",
        items=(item,),
    )

    assert result.submission_count == 1
    assert result.existing_count == 0
    assert result.new_count == 0
    assert result.supplement_count == 1
    assert result.error_count == 0
    assert (result.supplement_answer_count == 1)


def test_item_without_supplement_remains_existing():
    item = SubmissionImportItemResult(
        submission_index=1,
        supplier_tax_number="11102481-2-07",
        requester_tax_number="12345678",
        relation_id=274,
        plan=None,
        existing_submission_id=323,
        is_new=False,
        error=None,
    )

    assert item.exists is True
    assert item.is_supplement is False

def test_dry_run_detects_supplement_submission():
    writer = FakeWriter(
        existing_submission_id=None,
        supplement_existing_submission_id=323,
        supplement_has_answers=True,
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
    )
    result = orchestrator.run_dry_run(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert result.submission_count == 1
    assert result.existing_count == 0
    assert result.new_count == 0
    assert result.supplement_count == 1
    assert result.error_count == 0
    item = result.items[0]
    assert (item.existing_submission_id == 323)
    assert item.is_new is False
    assert item.is_supplement is True
    assert (item.supplement_answer_count == 1)
    assert (item.supplement_answer_value_count == 1)
    assert writer.preflight_calls == 1
    assert (writer.preflight_supplement_calls == 1)


def test_dry_run_treats_complete_legacy_candidate_as_existing():
    writer = FakeWriter(
        existing_submission_id=None,
        supplement_existing_submission_id=323,
        supplement_has_answers=False,
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
    )
    result = orchestrator.run_dry_run(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )
    assert result.existing_count == 1
    assert result.new_count == 0
    assert result.supplement_count == 0
    assert result.error_count == 0
    item = result.items[0]
    assert (item.existing_submission_id == 323)
    assert item.is_new is False
    assert item.is_supplement is False
    assert (writer.preflight_supplement_calls == 1)


def test_dry_run_remains_new_when_no_supplement_candidate_exists():
    writer = FakeWriter(
        existing_submission_id=None,
        supplement_existing_submission_id=None,
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
    )
    result = orchestrator.run_dry_run(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert result.existing_count == 0
    assert result.new_count == 1
    assert result.supplement_count == 0
    assert result.error_count == 0
    assert (writer.preflight_supplement_calls == 1)


def test_dry_run_does_not_check_supplement_when_normal_submission_exists():
    writer = FakeWriter(
        existing_submission_id=323,
        supplement_existing_submission_id=999,
        supplement_has_answers=True,
    )
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
    )
    result = orchestrator.run_dry_run(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert result.existing_count == 1
    assert result.new_count == 0
    assert result.supplement_count == 0
    assert writer.preflight_calls == 1
    assert (writer.preflight_supplement_calls == 0)

def create_supplement_orchestrator(
    *,
    import_writer=None,
    import_verifier=None,
):
    writer = FakeWriter(
        existing_submission_id=None,
        supplement_existing_submission_id=323,
        supplement_has_answers=True,
    )

    return SubmissionImportOrchestrator(
        context_reader=FakeContextReader(),
        submission_writer=writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )

def test_execute_supplements_writes_and_verifies():
    import_writer = FakeImportWriter(supplement_result=(FakeSupplementWriteResult(
                supplement_submission_count=1,
                answer_count=1,
                answer_value_count=1,
            )
        )
    )
    import_verifier = FakeImportVerifier(supplement_is_valid=True)
    orchestrator = (create_supplement_orchestrator(
            import_writer=import_writer,
            import_verifier=import_verifier,
        )
    )
    result = orchestrator.execute_supplements(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert (result.supplement_submission_count == 1)
    assert result.created_answer_count == 1
    assert (result.created_answer_value_count == 1)
    assert result.verification_succeeded is True
    assert (import_writer.write_supplement_items_calls == 1)
    assert (import_verifier.verify_supplement_items_calls == 1)


def test_execute_supplements_rejects_normal_new_submission():
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(),
        submission_writer=FakeWriter(
            existing_submission_id=None,
            supplement_existing_submission_id=None,),
        import_writer=FakeImportWriter(),
        import_verifier=FakeImportVerifier(),
    )
    with pytest.raises(
        ValueError,
        match="no supplement submissions",
    ):
        orchestrator.execute_supplements(
            payload=create_payload(),
            batch_id="BATCH_TEST",
        )


def test_execute_supplements_requires_import_writer():
    orchestrator = (create_supplement_orchestrator(
            import_writer=None,
            import_verifier=(FakeImportVerifier()),
        )
    )
    with pytest.raises(
        RuntimeError,
        match=("import_writer is required for supplement execute"),
    ):
        orchestrator.execute_supplements(
            payload=create_payload(),
            batch_id="BATCH_TEST",
        )


def test_execute_supplements_reports_failed_verification():
    import_writer = FakeImportWriter(supplement_result=(FakeSupplementWriteResult(
                supplement_submission_count=1,
                answer_count=1,
                answer_value_count=1,
            )
        )
    )
    import_verifier = FakeImportVerifier(supplement_is_valid=False)
    orchestrator = (create_supplement_orchestrator(
            import_writer=import_writer,
            import_verifier=import_verifier,
        )
    )
    result = orchestrator.execute_supplements(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )
    assert (result.verification_succeeded is False)
    assert result.verification_error is None


def test_execute_supplements_preserves_commit_result_when_verifier_fails():
    import_writer = FakeImportWriter(supplement_result=(FakeSupplementWriteResult(
                supplement_submission_count=1,
                answer_count=1,
                answer_value_count=1,
            )
        )
    )
    import_verifier = FakeImportVerifier(supplement_fail=True)
    orchestrator = (create_supplement_orchestrator(
            import_writer=import_writer,
            import_verifier=import_verifier,
        )
    )
    result = orchestrator.execute_supplements(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )
    assert (result.supplement_submission_count == 1)
    assert (result.verification_succeeded is False)
    assert (result.verification_error == "supplement verification failed")

def test_execute_existing_batch_reports_failed_written_verification():
    payload = create_payload()
    writer = FakeWriter(existing_submission_id=None)
    import_writer = FakeImportWriter(
        batch_created=False,
        submission_results=(
            FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )

    import_verifier = FakeImportVerifier(written_is_valid=False)
    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=True),
        submission_writer=writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )
    result = orchestrator.execute(
        payload=payload,
        batch_id="BATCH_TEST",
    )

    assert result.batch_created is False
    assert result.created_count == 1
    assert (result.verification_result is not None)
    assert (result.verification_succeeded is False)


def test_execute_existing_batch_preserves_commit_when_written_verifier_fails():
    writer = FakeWriter(existing_submission_id=None)

    import_writer = FakeImportWriter(
        batch_created=False,
        submission_results=(FakeWriteResult(
                submission_id=1001,
                created=True,
                answer_count=1,
                answer_value_count=1,
            ),
        ),
    )

    import_verifier = FakeImportVerifier(written_fail=True)

    orchestrator = SubmissionImportOrchestrator(
        context_reader=FakeContextReader(batch_exists=True),
        submission_writer=writer,
        import_writer=import_writer,
        import_verifier=import_verifier,
    )

    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )
    assert result.created_count == 1
    assert (result.verification_result is None)
    assert (result.verification_error == "written verification failed")
    assert (result.verification_succeeded is False)