from dataclasses import dataclass
import pytest
from alex.esg.services.submission_persistence_mapper import SubmissionPersistenceData
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan
from alex.esg.infrastructure.repositories.mssql_submission_import_writer import (
    MssqlSubmissionImportWriter,
    MssqlSubmissionSupplementWriteRequest,
)
from alex.esg.services.answer_value_persistence_mapper import AnswerValuePersistenceData
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceData

@dataclass(frozen=True)
class FakeBatchResult:
    created: bool

@dataclass(frozen=True)
class FakeSubmissionResult:
    submission_id: int
    created: bool
    answer_count: int
    answer_value_count: int

@dataclass(frozen=True)
class FakeSupplementResult:
    submission_id: int
    answer_count: int
    answer_value_count: int

class FakeCursor:
    pass

class FakeConnection:
    def __init__(self):
        self._cursor = FakeCursor()
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.commit_count = 0
        self.rollback_count = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True
        self.commit_count += 1

    def rollback(self):
        self.rolled_back = True
        self.rollback_count += 1

    def close(self):
        self.closed = True

class FakeConnectionFactory:
    def __init__(
        self,
        connection,
    ):
        self.connection = connection
    def connect(self):
        return self.connection

class FakeBatchWriter:
    def __init__(
        self,
        *,
        created=True,
        fail=False,
    ):
        self.created = created
        self.fail = fail
        self.calls = []

    def ensure_batch_on_cursor(
        self,
        cursor,
        *,
        batch_id,
        questionnaire_code,
        spec_version,
    ):
        self.calls.append(
            (
                cursor,
                batch_id,
                questionnaire_code,
                spec_version,
            )
        )
        if self.fail:
            raise RuntimeError("batch write failed")
        return FakeBatchResult(created=self.created)

class FakeSubmissionWriter:
    def __init__(
        self,
        *,
        results=(),
        fail=False,
        supplement_results=(),
        fail_on_supplement_call=None,
    ):
        self.results = tuple(results)
        self.fail = fail
        self.calls = []
        self.supplement_results = tuple(supplement_results)
        self.fail_on_supplement_call = (fail_on_supplement_call)

        self.supplement_calls = []
    def write_many_on_cursor(
        self,
        cursor,
        plans,
    ):
        self.calls.append(
            (
                cursor,
                plans,
            )
        )

        if self.fail:
            raise RuntimeError("submission write failed")
        return self.results

    def supplement_answers_on_cursor(
        self,
        cursor,
        submission_id,
        answers,
    ):
        self.supplement_calls.append(
            (
                cursor,
                submission_id,
                answers,
            )
        )

        call_number = len(self.supplement_calls)

        if (self.fail_on_supplement_call == call_number
        ):
            raise RuntimeError("supplement write failed")
        if self.supplement_results:
            return self.supplement_results[call_number - 1]

        return FakeSupplementResult(
            submission_id=submission_id,
            answer_count=len(answers),
            answer_value_count=sum(len(answer.values) for answer in answers),
        )

def create_plan(
    batch_id="BATCH_TEST",
):
    submission = (SubmissionPersistenceData(
            batch_id=batch_id,
            relation_id=123,
            external_supplier_key=("SUP_12345678"),
            respondent_id=("RESP_12345678_2026"),
            respondent_mp_id=None,
            org_size=None,
            submitted_at=None,
            status="imported_complete",
            raw_payload="{}",
        )
    )
    return SubmissionPersistencePlan(
        submission=submission,
        answers=(),
        skipped_question_ids=(),
    )

def create_supplement_answer():
    value = AnswerValuePersistenceData(
        field_type="text",
        option_id=None,
        selected=None,
        number_value=None,
        text_value="supplement",
    )

    return SubmissionAnswerPersistenceData(
        question_id="034FEA08_DETAIL1",
        values=(value,),
    )

def test_import_writer_commits_new_batch_and_submission():
    connection = FakeConnection()
    batch_writer = FakeBatchWriter( created=True)
    submission_writer = (FakeSubmissionWriter(
            results=(FakeSubmissionResult(
                    submission_id=1001,
                    created=True,
                    answer_count=200,
                    answer_value_count=888,
                ),
            )
        )
    )
    writer = (MssqlSubmissionImportWriter(
            connection_factory=(FakeConnectionFactory(connection)),
            batch_writer=batch_writer,
            submission_writer=(submission_writer),
        )
    )
    plan = create_plan()
    result = writer.write(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[plan,],
    )
    assert result.batch_created is True
    assert (result.created_submission_count == 1)
    assert (result.existing_submission_count == 0)
    assert (result.created_answer_count == 200)
    assert (result.created_answer_value_count == 888)
    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True

def test_import_writer_reuses_existing_batch():
    connection = FakeConnection()
    batch_writer = FakeBatchWriter(created=False)
    submission_writer = (
        FakeSubmissionWriter(
            results=(
                FakeSubmissionResult(
                    submission_id=323,
                    created=False,
                    answer_count=0,
                    answer_value_count=0,
                ),
            )
        )
    )
    writer = (MssqlSubmissionImportWriter(
            connection_factory=(FakeConnectionFactory(connection)),
            batch_writer=batch_writer,
            submission_writer=(submission_writer),
        )
    )
    result = writer.write(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )
    assert result.batch_created is False
    assert (result.created_submission_count == 0)
    assert (result.existing_submission_count == 1)
    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True


def test_import_writer_uses_same_cursor():
    connection = FakeConnection()
    batch_writer = FakeBatchWriter()
    submission_writer = (FakeSubmissionWriter())
    writer = (MssqlSubmissionImportWriter(
            connection_factory=(FakeConnectionFactory(connection)),
            batch_writer=batch_writer,
            submission_writer=( submission_writer),
        )
    )
    writer.write(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )
    batch_cursor = (batch_writer.calls[0][0])
    submission_cursor = (submission_writer.calls[0][0])
    assert (batch_cursor is submission_cursor)
    assert (batch_cursor is connection._cursor)

def test_import_writer_rolls_back_when_batch_fails():
    connection = FakeConnection()
    writer = (MssqlSubmissionImportWriter(
            connection_factory=(FakeConnectionFactory(connection)),
            batch_writer=(FakeBatchWriter(fail=True)),
            submission_writer=(FakeSubmissionWriter()),
        )
    )

    with pytest.raises(
        RuntimeError,
        match="batch write failed",
    ):
        writer.write(
            batch_id="BATCH_TEST",
            questionnaire_code="SZTFH",
            spec_version="2.0",
            plans=[create_plan(),],
        )
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True

def test_import_writer_rolls_back_when_submission_fails():
    connection = FakeConnection()
    writer = (MssqlSubmissionImportWriter(
            connection_factory=(FakeConnectionFactory(connection)),
            batch_writer=(FakeBatchWriter()),
            submission_writer=(FakeSubmissionWriter(fail=True)),
        )
    )
    with pytest.raises(
        RuntimeError,
        match="submission write failed",
    ):
        writer.write(
            batch_id="BATCH_TEST",
            questionnaire_code="SZTFH",
            spec_version="2.0",
            plans=[create_plan(),],
        )
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True

def test_import_writer_rejects_plan_from_other_batch():
    connection = FakeConnection()

    writer = (MssqlSubmissionImportWriter(connection_factory=(FakeConnectionFactory(connection)
            ),
            batch_writer=(FakeBatchWriter()),
            submission_writer=(FakeSubmissionWriter()),
        )
    )
    with pytest.raises(
        ValueError,
        match="plan batch_id",
    ):
        writer.write(
            batch_id="BATCH_A",
            questionnaire_code="SZTFH",
            spec_version="2.0",
            plans=[create_plan(batch_id="BATCH_B"),],
        )
    assert connection.committed is False
    assert connection.rolled_back is False

def test_import_writer_rollback_mode_never_commits():
    connection = FakeConnection()

    batch_writer = FakeBatchWriter(
        created=True
    )

    submission_writer = (
        FakeSubmissionWriter(
            results=(
                FakeSubmissionResult(
                    submission_id=1001,
                    created=True,
                    answer_count=200,
                    answer_value_count=888,
                ),
            )
        )
    )

    writer = MssqlSubmissionImportWriter(
        connection_factory=(
            FakeConnectionFactory(
                connection
            )
        ),
        batch_writer=batch_writer,
        submission_writer=(
            submission_writer
        ),
    )

    result = writer.write_rollback(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[
            create_plan(),
        ],
    )
    assert result.batch_created is True
    assert (result.created_submission_count == 1)
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True
    assert len(batch_writer.calls) == 1
    assert len(submission_writer.calls) == 1

def test_import_writer_commits_supplements_atomically():
    connection = FakeConnection()

    submission_writer = FakeSubmissionWriter(
        supplement_results=(
            FakeSupplementResult(
                submission_id=760,
                answer_count=1,
                answer_value_count=1,
            ),
            FakeSupplementResult(
                submission_id=761,
                answer_count=1,
                answer_value_count=1,
            ),
        )
    )

    writer = MssqlSubmissionImportWriter(
        connection_factory=(
            FakeConnectionFactory(
                connection
            )
        ),
        batch_writer=FakeBatchWriter(),
        submission_writer=(
            submission_writer
        ),
    )

    answer = create_supplement_answer()

    result = writer.write_supplements(
        requests=[
            MssqlSubmissionSupplementWriteRequest(
                submission_id=760,
                answers=(
                    answer,
                ),
            ),
            MssqlSubmissionSupplementWriteRequest(
                submission_id=761,
                answers=(
                    answer,
                ),
            ),
        ]
    )

    assert (
        result.supplement_submission_count
        == 2
    )

    assert result.answer_count == 2
    assert result.answer_value_count == 2

    assert connection.commit_count == 1
    assert connection.rollback_count == 0
    assert connection.closed is True

    assert len(
        submission_writer.supplement_calls
    ) == 2

    assert (
        submission_writer
        .supplement_calls[0][0]
        is connection._cursor
    )

    assert (
        submission_writer
        .supplement_calls[1][0]
        is connection._cursor
    )


def test_import_writer_rolls_back_all_supplements_on_error():
    connection = FakeConnection()

    submission_writer = FakeSubmissionWriter(
        fail_on_supplement_call=2
    )

    writer = MssqlSubmissionImportWriter(
        connection_factory=(
            FakeConnectionFactory(
                connection
            )
        ),
        batch_writer=FakeBatchWriter(),
        submission_writer=(
            submission_writer
        ),
    )

    answer = create_supplement_answer()

    with pytest.raises(
        RuntimeError,
        match="supplement write failed",
    ):
        writer.write_supplements(
            requests=[
                MssqlSubmissionSupplementWriteRequest(
                    submission_id=760,
                    answers=(
                        answer,
                    ),
                ),
                MssqlSubmissionSupplementWriteRequest(
                    submission_id=761,
                    answers=(
                        answer,
                    ),
                ),
            ]
        )

    assert connection.commit_count == 0
    assert connection.rollback_count == 1
    assert connection.closed is True

    assert len(
        submission_writer.supplement_calls
    ) == 2


def test_import_writer_rejects_duplicate_supplement_submission():
    connection = FakeConnection()

    submission_writer = FakeSubmissionWriter()

    writer = MssqlSubmissionImportWriter(
        connection_factory=(
            FakeConnectionFactory(
                connection
            )
        ),
        batch_writer=FakeBatchWriter(),
        submission_writer=(
            submission_writer
        ),
    )

    answer = create_supplement_answer()

    with pytest.raises(
        ValueError,
        match=(
            "duplicate supplement "
            "submission_id"
        ),
    ):
        writer.write_supplements(
            requests=[
                MssqlSubmissionSupplementWriteRequest(
                    submission_id=760,
                    answers=(
                        answer,
                    ),
                ),
                MssqlSubmissionSupplementWriteRequest(
                    submission_id=760,
                    answers=(
                        answer,
                    ),
                ),
            ]
        )

    assert connection.commit_count == 0
    assert connection.rollback_count == 0

    assert len(
        submission_writer.supplement_calls
    ) == 0


def test_import_writer_supplement_rollback_mode_never_commits():
    connection = FakeConnection()

    submission_writer = FakeSubmissionWriter()

    writer = MssqlSubmissionImportWriter(
        connection_factory=(
            FakeConnectionFactory(
                connection
            )
        ),
        batch_writer=FakeBatchWriter(),
        submission_writer=(
            submission_writer
        ),
    )

    answer = create_supplement_answer()

    result = writer.write_supplements_rollback(
        requests=[
            MssqlSubmissionSupplementWriteRequest(
                submission_id=760,
                answers=(
                    answer,
                ),
            ),
            MssqlSubmissionSupplementWriteRequest(
                submission_id=761,
                answers=(
                    answer,
                ),
            ),
        ]
    )

    assert (
        result.supplement_submission_count
        == 2
    )

    assert connection.commit_count == 0
    assert connection.rollback_count == 1
    assert connection.closed is True