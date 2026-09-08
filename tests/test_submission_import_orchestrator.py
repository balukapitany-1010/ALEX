from dataclasses import dataclass
from alex.esg.services.submission_import_orchestrator import SubmissionImportOrchestrator
from copy import deepcopy

@dataclass(frozen=True)
class FakeContext:
    questionnaire_code: str
    spec_version: str
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

class FakeContextReader:
    def __init__(
            self,
            relation_id=274,
            relation_ids_by_supplier_tax=None,
    ):
        self.relation_id = relation_id
        self.relation_ids_by_supplier_tax = (
            relation_ids_by_supplier_tax
        )

    def load_context(
        self,
        *,
        batch_id,
        questionnaire_code,
        spec_version,
    ):
        return FakeContext(
            questionnaire_code=(questionnaire_code),
            spec_version=(spec_version),
            batch_id=batch_id,
            questionnaire_question_ids=(frozenset({"TEST_Q",})),
            option_ids_by_question={"TEST_Q": frozenset({"TEST_Q_1",})},
        )

    def resolve_relation_id(
            self,
            *,
            requester_tax_number,
            supplier_tax_number,
    ):
        if (
                self.relation_ids_by_supplier_tax
                is not None
        ):
            return (
                self.relation_ids_by_supplier_tax[
                    supplier_tax_number
                ]
            )

        return self.relation_id

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
    ):
        self.existing_submission_id = (
            existing_submission_id
        )

        self.existing_submission_ids_by_relation = (
            existing_submission_ids_by_relation
        )

        self.preflight_calls = 0
        self.write_many_calls = 0
        self.write_many_plans = None

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

    second_submission = deepcopy(
        payload["submissions"][0]
    )

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
    ][
        "period"
    ] = "2024"

    payload[
        "submissions"
    ].append(
        second_submission
    )

    return payload


def test_dry_run_reports_existing_submission():
    writer = FakeWriter(existing_submission_id=323)

    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
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

    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
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
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
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
    writer = FakeWriter(
        existing_submission_id=None
    )

    orchestrator = (
        SubmissionImportOrchestrator(
            context_reader=(
                FakeContextReader()
            ),
            submission_writer=writer,
        )
    )

    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert writer.write_many_calls == 1

    assert len(
        writer.write_many_plans
    ) == 1

    assert result.created_count == 1
    assert result.existing_count == 0

    assert (
        result.created_answer_count
        == 1
    )

    assert (
        result.created_answer_value_count
        == 1
    )


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

    orchestrator = (
        SubmissionImportOrchestrator(
            context_reader=(
                FakeContextReader()
            ),
            submission_writer=writer,
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

    assert writer.write_many_calls == 0

def test_execute_reports_existing_submission():
    writer = FakeWriter(existing_submission_id=323)
    orchestrator = (SubmissionImportOrchestrator(
            context_reader=(FakeContextReader()),
            submission_writer=writer,
        )
    )

    result = orchestrator.execute(
        payload=create_payload(),
        batch_id="BATCH_TEST",
    )

    assert writer.write_many_calls == 1
    assert result.created_count == 0
    assert result.existing_count == 1
    assert (result.created_answer_count == 0)
    assert (result.created_answer_value_count == 0)

def test_execute_handles_existing_and_new_submissions():
    payload = create_mixed_payload()

    context_reader = (
        FakeContextReader(
            relation_ids_by_supplier_tax={
                "11102481207": 274,
                "10654411243": 275,
            }
        )
    )

    writer = FakeWriter(
        existing_submission_ids_by_relation={
            274: 323,
            275: None,
        }
    )

    orchestrator = (
        SubmissionImportOrchestrator(
            context_reader=(
                context_reader
            ),
            submission_writer=writer,
        )
    )

    result = orchestrator.execute(
        payload=payload,
        batch_id="BATCH_TEST",
    )

    assert result.dry_run.submission_count == 2
    assert result.dry_run.existing_count == 1
    assert result.dry_run.new_count == 1
    assert result.dry_run.error_count == 0
    assert writer.write_many_calls == 1
    assert len(writer.write_many_plans) == 2
    assert result.created_count == 1
    assert result.existing_count == 1
    assert (result.created_answer_count == 1)
    assert (result.created_answer_value_count == 1)
    assert (result.write_results[0].submission_id == 323)
    assert (result.write_results[0].created is False)
    assert (result.write_results[1].created is True)

