from decimal import Decimal
import pytest
from alex.esg.infrastructure.repositories.mssql_submission_writer import  MssqlSubmissionWriter
from alex.esg.services.answer_value_persistence_mapper import AnswerValuePersistenceData
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceData
from alex.esg.services.submission_persistence_mapper import SubmissionPersistenceData
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan


class FakeCursor:
    def __init__(
        self,
        *,
        batch_exists=True,
        existing_submission_id=None,
        fail_on_answer_value=False,
    ):
        self.batch_exists = batch_exists
        self.existing_submission_id = (existing_submission_id)
        self.fail_on_answer_value = (fail_on_answer_value)
        self.executed = []
        self._rows = []
        self._next_answer_id = 2000

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
            if self.batch_exists:
                self._rows = [("BATCH_TEST",)]
            else:
                self._rows = []

        elif (
            "FROM dbo.SUBMISSION" in normalized_sql and "SELECT" in normalized_sql
        ):
            if (
                self.existing_submission_id
                is None
            ):
                self._rows = []
            else:
                self._rows = [
                    (self.existing_submission_id, )
                ]

        elif (
            "INSERT INTO dbo.SUBMISSION " in normalized_sql
        ):
            self._rows = [
                (1001,)
            ]

        elif (
            "INSERT INTO "
            "dbo.SUBMISSION_ANSWER"
            in normalized_sql
        ):
            self._next_answer_id += 1

            self._rows = [
                (
                    self._next_answer_id,
                )
            ]

        elif (
            "INSERT INTO dbo.ANSWER_VALUE" in normalized_sql
        ):
            if self.fail_on_answer_value:
                raise RuntimeError("simulated database error")

            self._rows = []

        else:
            self._rows = []

        return self

    def fetchone(self):
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


def create_plan():
    submission = (
        SubmissionPersistenceData(
            batch_id="BATCH_TEST",
            relation_id=274,
            external_supplier_key=("SUP_11102481207"),
            respondent_id=( "RESP_11102481207_2024"),
            respondent_mp_id=None,
            org_size=None,
            submitted_at=None,
            status="imported_complete",
            raw_payload="{}",
        )
    )

    values = (AnswerValuePersistenceData(
            field_type="number",
            option_id="0364FD79_1",
            selected=None,
            number_value=Decimal("53.9500"),
            text_value=None,
        ),
    )

    answers = (SubmissionAnswerPersistenceData(
            question_id="0364FD79",
            values=values,
        ),
    )

    return SubmissionPersistencePlan(
        submission=submission,
        answers=answers,
        skipped_question_ids=(),
    )


def test_writer_inserts_complete_submission():
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))
    result = writer.write(create_plan())
    assert result.created is True
    assert (result.submission_id == 1001)
    assert result.answer_count == 1
    assert (result.answer_value_count == 1)
    assert connection.committed is True
    assert connection.rolled_back is False
    assert connection.closed is True

    sql_statements = [
        sql
        for (
            sql,
            params,
        ) in cursor.executed
    ]
    assert any("INSERT INTO dbo.SUBMISSION " in sql for sql in sql_statements)
    assert any("INSERT INTO " "dbo.SUBMISSION_ANSWER" in sql for sql in sql_statements)
    assert any("INSERT INTO dbo.ANSWER_VALUE" in sql for sql in sql_statements)


def test_writer_does_not_duplicate_submission():
    cursor = FakeCursor(existing_submission_id=323)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))
    result = writer.write(create_plan())
    assert result.created is False
    assert (result.submission_id == 323)
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True
    assert not any("INSERT INTO dbo.SUBMISSION " in sql for (
            sql,
            params,
        ) in cursor.executed
    )


def test_writer_rejects_missing_batch():
    cursor = FakeCursor(batch_exists=False)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))
    with pytest.raises(
        ValueError,
        match="SUBMISSION_BATCH does not exist",
    ):
        writer.write(create_plan())
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True


def test_writer_rolls_back_on_answer_value_error():
    cursor = FakeCursor(fail_on_answer_value=True)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))

    with pytest.raises(
        RuntimeError,
        match="simulated database error",
    ):
        writer.write( create_plan())
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True

def test_preflight_finds_existing_submission_without_writing():
    cursor = FakeCursor(existing_submission_id=323)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))
    result = writer.preflight(create_plan())
    assert result.exists is True
    assert result.can_insert is False
    assert (result.existing_submission_id == 323)
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True
    assert not any(
        "INSERT INTO" in sql
        for (
            sql,
            params,
        ) in cursor.executed
    )


def test_preflight_reports_new_submission_without_inserting():
    cursor = FakeCursor(existing_submission_id=None)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))
    result = writer.preflight(create_plan())
    assert result.exists is False
    assert result.can_insert is True
    assert (result.existing_submission_id is None)
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True
    assert not any(
        "INSERT INTO" in sql
        for (
            sql,
            params,
        ) in cursor.executed
    )


def test_preflight_rejects_missing_batch():
    cursor = FakeCursor(batch_exists=False)
    connection = FakeConnection(cursor)
    writer = MssqlSubmissionWriter(FakeConnectionFactory(connection))

    with pytest.raises(
        ValueError,
        match="SUBMISSION_BATCH does not exist",
    ):
        writer.preflight(create_plan())
    assert connection.committed is False
    assert connection.rolled_back is True
    assert connection.closed is True

    assert not any("INSERT INTO" in sql for (
            sql,
            params,
        ) in cursor.executed)