from alex.esg.infrastructure.repositories.mssql_submission_import_verifier import MssqlSubmissionImportVerifier
from alex.esg.services.submission_persistence_mapper import SubmissionPersistenceData
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan

class FakeCursor:
    def __init__(
        self,
        *,
        batch_row=("SZTFH", "2.0"),
        submission_count=1,
        answer_count=2,
        answer_value_count=3,
    ):
        self.batch_row = batch_row
        self.submission_count = (submission_count)
        self.answer_count = (answer_count)
        self.answer_value_count = (answer_value_count)
        self._result = None

    def execute(
        self,
        sql,
        *params,
    ):
        normalized_sql = " ".join(sql.split())

        if (
            "FROM dbo.SUBMISSION_BATCH" in normalized_sql
        ):
            self._result = (self.batch_row)

        elif ("FROM dbo.SUBMISSION_ANSWER AS sa" in normalized_sql and "dbo.ANSWER_VALUE" not in normalized_sql
        ):
            self._result = (self.answer_count,)

        elif ("FROM dbo.ANSWER_VALUE AS av" in normalized_sql
        ):
            self._result = (self.answer_value_count,)

        elif ("FROM dbo.SUBMISSION" in normalized_sql):
            self._result = (self.submission_count,)

        else:
            raise AssertionError(normalized_sql)

        return self

    def fetchone(
        self,
    ):
        return self._result


class FakeConnection:
    def __init__(
        self,
        cursor,
    ):
        self._cursor = cursor
        self.rolled_back = False
        self.closed = False

    def cursor(
        self,
    ):
        return self._cursor

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


def create_plan(
    *,
    batch_id="BATCH_TEST",
    answer_count=2,
    answer_value_count=3,
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

    class FakeAnswer:
        def __init__(
            self,
            value_count,
        ):
            self.values = tuple(object()
                for _ in range(value_count))

    answers = []
    remaining_values = (answer_value_count)
    for index in range(answer_count):
        if index == 0:
            value_count = (remaining_values)
        else:
            value_count = 0
        answers.append(FakeAnswer(value_count))
        remaining_values -= (value_count)

    return SubmissionPersistencePlan(
        submission=submission,
        answers=tuple(answers),
        skipped_question_ids=(),
    )


def test_verifier_accepts_matching_new_batch():
    cursor = FakeCursor(
        batch_row=(
            "SZTFH",
            "2.0",
        ),
        submission_count=1,
        answer_count=2,
        answer_value_count=3,
    )
    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))
    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )

    assert result.is_valid is True
    assert result.batch_exists is True
    assert (result.questionnaire_matches is True)
    assert (result.submission_count_matches is True)
    assert (result.answer_count_matches is True)
    assert (result.answer_value_count_matches is True)
    assert connection.rolled_back is True
    assert connection.closed is True


def test_verifier_detects_wrong_submission_count():
    cursor = FakeCursor(
        submission_count=2,
        answer_count=2,
        answer_value_count=3,
    )

    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))
    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )
    assert result.is_valid is False
    assert (result.submission_count_matches is False)

def test_verifier_detects_wrong_answer_count():
    cursor = FakeCursor(answer_count=999)
    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))

    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )
    assert result.is_valid is False
    assert (result.answer_count_matches is False)


def test_verifier_detects_wrong_answer_value_count():
    cursor = FakeCursor(answer_value_count=999)
    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))
    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )

    assert result.is_valid is False
    assert (result.answer_value_count_matches is False)

def test_verifier_detects_wrong_questionnaire():
    cursor = FakeCursor(
        batch_row=(
            "SZTFH",
            "2.1",
        )
    )
    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))

    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )
    assert result.is_valid is False
    assert (result.questionnaire_matches is False)

def test_verifier_detects_missing_batch():
    cursor = FakeCursor(
        batch_row=None,
        submission_count=0,
        answer_count=0,
        answer_value_count=0,
    )

    connection = FakeConnection(cursor)
    verifier = (MssqlSubmissionImportVerifier(FakeConnectionFactory(connection)))
    result = verifier.verify_new_batch(
        batch_id="BATCH_TEST",
        questionnaire_code="SZTFH",
        spec_version="2.0",
        plans=[create_plan(),],
    )

    assert result.is_valid is False
    assert result.batch_exists is False