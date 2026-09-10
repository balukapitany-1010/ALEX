from dataclasses import dataclass
import pytest
from alex.esg.infrastructure.repositories.mssql_submission_import_writer import MssqlSubmissionImportWriter
from alex.esg.services.submission_persistence_mapper import SubmissionPersistenceData
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan

@dataclass(frozen=True)
class FakeBatchResult:
    created: bool

@dataclass(frozen=True)
class FakeSubmissionResult:
    submission_id: int
    created: bool
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

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

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
    ):
        self.results = tuple(results)
        self.fail = fail
        self.calls = []
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