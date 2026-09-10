import pytest
from alex.esg.infrastructure.repositories.mssql_submission_batch_writer import MssqlSubmissionBatchWriter

class FakeCursor:
    def __init__(
        self,
        *,
        existing_batch=None,
        questionnaire_exists=True,
        fail_on_insert=False,
    ):
        self.existing_batch = (existing_batch)
        self.questionnaire_exists = (questionnaire_exists)
        self.fail_on_insert = (fail_on_insert)
        self.executed = []
        self._rows = []

    def execute(
        self,
        sql,
        *params,
    ):
        normalized_sql = " ".join(sql.split())

        self.executed.append(
            (
                normalized_sql,
                params,
            )
        )

        if (
            "FROM dbo.SUBMISSION_BATCH" in normalized_sql
        ):
            if self.existing_batch is None:
                self._rows = []
            else:
                self._rows = [self.existing_batch]

        elif (
            "FROM dbo.QUESTIONNAIRE" in normalized_sql
        ):
            if self.questionnaire_exists:
                self._rows = [(1,)]
            else:
                self._rows = []

        elif (
            "INSERT INTO dbo.SUBMISSION_BATCH" in normalized_sql
        ):
            if self.fail_on_insert:
                raise RuntimeError("simulated database error")
            self._rows = []
        return self
    def fetchone(
        self,
    ):
        if not self._rows:
            return None
        return self._rows.pop(0)


class FakeConnection:
    def __init__(
        self,
        cursor,
    ):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(
        self,
    ):
        return self._cursor

    def commit(
        self,
    ):
        self.committed = True

    def rollback(
        self,
    ):
        self.rolled_back = True

    def close(
        self,
    ):
        self.closed = True

class FakeConnectionFactory:
    def __init__(
        self,
        connection,
    ):
        self.connection = connection

    def connect(
        self,
    ):
        return self.connection


def test_creates_new_batch():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))
    result = writer.ensure_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
    )

    assert result.batch_id == "BATCH_TEST"
    assert result.created is True
    assert result.questionnaire_code == "SZTFH"
    assert result.spec_version == "2.0"
    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True
    assert any("INSERT INTO dbo.SUBMISSION_BATCH" in sql for (
            sql,
            params,
        ) in cursor.executed)


def test_reuses_existing_matching_batch():
    cursor = FakeCursor(existing_batch=(
            "SZTFH",
            "2.0",
        )
    )

    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))
    result = writer.ensure_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
    )

    assert result.created is False
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True
    assert not any("INSERT INTO dbo.SUBMISSION_BATCH" in sql for (
            sql,
            params,
        ) in cursor.executed)


def test_rejects_existing_batch_with_other_version():
    cursor = FakeCursor(existing_batch=(
            "SZTFH",
            "2.1",
        )
    )
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))

    with pytest.raises(
        ValueError,
        match="does not match import",
    ):
        writer.ensure_batch(
            batch_id="BATCH_TEST",
            questionnaire_code="SZTFH",
            spec_version="2.0",
        )

    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True


def test_rejects_missing_questionnaire():
    cursor = FakeCursor(questionnaire_exists=False)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))

    with pytest.raises(
        ValueError,
        match="QUESTIONNAIRE does not exist",
    ):
        writer.ensure_batch(
            batch_id="BATCH_TEST",
            questionnaire_code="SZTFH",
            spec_version="9.9",
        )

    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True

    assert not any("INSERT INTO dbo.SUBMISSION_BATCH" in sql for (
            sql,
            params,
        ) in cursor.executed)


def test_rolls_back_when_insert_fails():
    cursor = FakeCursor(fail_on_insert=True)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))

    with pytest.raises(
        RuntimeError,
        match="simulated database error",
    ):
        writer.ensure_batch(
            batch_id="BATCH_TEST",
            questionnaire_code="SZTFH",
            spec_version="2.0",
        )
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True


def test_new_batch_lookup_uses_locks():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionBatchWriter(FakeConnectionFactory(connection))

    writer.ensure_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
    )

    executed_sql = "\n".join( sql for (
            sql,
            params,
        ) in cursor.executed
    )

    assert "UPDLOCK" in executed_sql
    assert "HOLDLOCK" in executed_sql