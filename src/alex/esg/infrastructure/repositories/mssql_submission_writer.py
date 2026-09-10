from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan


@dataclass(frozen=True)
class MssqlSubmissionWriteResult:
    submission_id: int
    created: bool
    answer_count: int
    answer_value_count: int

@dataclass(frozen=True)
class MssqlSubmissionPreflightResult:
    batch_id: str
    existing_submission_id: int | None

    @property
    def exists(self) -> bool:
        return (self.existing_submission_id is not None)

    @property
    def can_insert(self) -> bool:
        return not self.exists


class MssqlSubmissionWriter:
    def __init__(
        self,
        connection_factory,
    ) -> None:
        self._next_submission_id = 1000
        if connection_factory is None:
            raise ValueError("connection_factory is required")

        self._connection_factory = (connection_factory)

    def preflight(
        self,
        plan: SubmissionPersistencePlan,
    ) -> MssqlSubmissionPreflightResult:
        if not isinstance(
            plan,
            SubmissionPersistencePlan,
        ):
            raise TypeError(
                "plan must be a "
                "SubmissionPersistencePlan"
            )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            self._ensure_batch_exists(
                cursor,
                plan.submission.batch_id,
            )

            existing_submission_id = (
                self._find_existing_submission_id_read_only(
                    cursor,
                    plan,
                )
            )

            connection.rollback()

            return (
                MssqlSubmissionPreflightResult(
                    batch_id=(plan.submission.batch_id),
                    existing_submission_id=(existing_submission_id),
                )
            )

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def write(
        self,
        plan: SubmissionPersistencePlan,
    ) -> MssqlSubmissionWriteResult:
        if not isinstance(
            plan,
            SubmissionPersistencePlan,
        ):
            raise TypeError(
                "plan must be a "
                "SubmissionPersistencePlan"
            )

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            self._ensure_batch_exists(
                cursor,
                plan.submission.batch_id,
            )

            existing_submission_id = (
                self._find_existing_submission_id_for_write(
                    cursor,
                    plan,
                )
            )

            if existing_submission_id is not None:
                connection.rollback()

                return MssqlSubmissionWriteResult(
                    submission_id=(
                        existing_submission_id
                    ),
                    created=False,
                    answer_count=0,
                    answer_value_count=0,
                )

            submission_id = (
                self._insert_submission(
                    cursor,
                    plan,
                )
            )

            answer_count = 0
            answer_value_count = 0

            for answer in plan.answers:
                submission_answer_id = (
                    self._insert_submission_answer(
                        cursor,
                        submission_id,
                        answer.question_id,
                    )
                )

                answer_count += 1

                for value in answer.values:
                    self._insert_answer_value(
                        cursor,
                        submission_answer_id,
                        value,
                    )

                    answer_value_count += 1

            connection.commit()

            return MssqlSubmissionWriteResult(
                submission_id=submission_id,
                created=True,
                answer_count=answer_count,
                answer_value_count=(
                    answer_value_count
                ),
            )

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
    def write_many(
        self,
        plans: list[SubmissionPersistencePlan],
    ) -> tuple[
        MssqlSubmissionWriteResult,
        ...
    ]:
        if not isinstance(
            plans,
            list,
        ):
            raise TypeError("plans must be a list")
        if not plans:
            return ()
        for plan in plans:
            if not isinstance(
                plan,
                SubmissionPersistencePlan,
            ):
                raise TypeError("all plans must be SubmissionPersistencePlan")
        batch_ids = {plan.submission.batch_id for plan in plans}
        if len(batch_ids) != 1:
            raise ValueError("all plans must belong to the same batch")
        batch_id = next(iter(batch_ids))
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            results = self.write_many_on_cursor(
                cursor,
                plans,
            )
            connection.commit()

            return results

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def write_many_on_cursor(
            self,
            cursor,
            plans: list[
                SubmissionPersistencePlan
            ],
    ) -> tuple[
        MssqlSubmissionWriteResult,
        ...
    ]:
        if not isinstance(
                plans,
                list,
        ):
            raise TypeError("plans must be a list")

        if not plans:
            return ()

        for plan in plans:
            if not isinstance(
                    plan,
                    SubmissionPersistencePlan,
            ):
                raise TypeError("all plans must be SubmissionPersistencePlan")

        batch_ids = {plan.submission.batch_id for plan in plans}

        if len(batch_ids) != 1:
            raise ValueError("all plans must belong to the same batch")

        batch_id = next(iter(batch_ids) )

        self._ensure_batch_exists(
            cursor,
            batch_id,
        )

        results = []

        for plan in plans:
            existing_submission_id = (self._find_existing_submission_id_for_write(
                    cursor,
                    plan,
                )
            )

            if existing_submission_id is not None:
                results.append(MssqlSubmissionWriteResult(
                        submission_id=(existing_submission_id),
                        created=False,
                        answer_count=0,
                        answer_value_count=0,
                    )
                )

                continue

            submission_id = (
                self._insert_submission(
                    cursor,
                    plan,
                )
            )

            answer_count = 0
            answer_value_count = 0

            for answer in plan.answers:
                submission_answer_id = (
                    self._insert_submission_answer(
                        cursor,
                        submission_id,
                        answer.question_id,
                    )
                )

                answer_count += 1

                for value in answer.values:
                    self._insert_answer_value(
                        cursor,
                        submission_answer_id,
                        value,
                    )

                    answer_value_count += 1

            results.append(MssqlSubmissionWriteResult(
                    submission_id=(submission_id),
                    created=True,
                    answer_count=(answer_count),
                    answer_value_count=(answer_value_count),
                )
            )

        return tuple(results)

    @staticmethod
    def _ensure_batch_exists(
        cursor,
        batch_id: str,
    ) -> None:
        cursor.execute(
            """
            SELECT
                batch_id
            FROM dbo.SUBMISSION_BATCH
            WHERE batch_id = ?
            """,
            batch_id,
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("SUBMISSION_BATCH does not exist: " f"{batch_id}")

    @staticmethod
    def _normalize_respondent_id_for_match(
            value,
    ) -> str:
        if value is None:
            return ""

        text = str(
            value
        ).strip().upper()

        if not text:
            return ""

        # Csak az ALEX/legacy generált RESP_ azonosítókat
        # normalizáljuk agresszíven.
        # Külső, saját respondent_id-ket nem alakítunk át.
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
    def _find_matching_submission_id(
            cls,
            cursor,
            expected_respondent_id,
    ) -> int | None:
        expected = (
            cls._normalize_respondent_id_for_match(
                expected_respondent_id
            )
        )

        matching_submission_ids = []

        while True:
            row = cursor.fetchone()

            if row is None:
                break

            actual = (
                cls._normalize_respondent_id_for_match(
                    row[1]
                )
            )

            if actual == expected:
                matching_submission_ids.append(
                    int(row[0])
                )

        if not matching_submission_ids:
            return None

        if len(
                matching_submission_ids
        ) > 1:
            raise RuntimeError(
                "multiple matching submissions "
                "already exist: "
                f"{matching_submission_ids}"
            )

        return matching_submission_ids[0]

    @classmethod
    def _find_existing_submission_id_read_only(
            cls,
            cursor,
            plan: SubmissionPersistencePlan,
    ) -> int | None:
        submission = plan.submission

        cursor.execute(
            """
            SELECT
                submission_id,
                respondent_id
            FROM dbo.SUBMISSION
            WHERE batch_id = ?
              AND relation_id = ?
              AND (
                    respondent_mp_id = ?
                    OR (
                        respondent_mp_id IS NULL
                        AND ? IS NULL
                    )
                  )
            ORDER BY submission_id
            """,
            submission.batch_id,
            submission.relation_id,
            submission.respondent_mp_id,
            submission.respondent_mp_id,
        )

        return cls._find_matching_submission_id(
            cursor,
            submission.respondent_id,
        )

    @classmethod
    def _find_existing_submission_id_for_write(
            cls,
            cursor,
            plan: SubmissionPersistencePlan,
    ) -> int | None:
        submission = plan.submission

        cursor.execute(
            """
            SELECT
                submission_id,
                respondent_id
            FROM dbo.SUBMISSION WITH (
                UPDLOCK,
                HOLDLOCK
            )
            WHERE batch_id = ?
              AND relation_id = ?
              AND (
                    respondent_mp_id = ?
                    OR (
                        respondent_mp_id IS NULL
                        AND ? IS NULL
                    )
                  )
            ORDER BY submission_id
            """,
            submission.batch_id,
            submission.relation_id,
            submission.respondent_mp_id,
            submission.respondent_mp_id,
        )

        return cls._find_matching_submission_id(
            cursor,
            submission.respondent_id,
        )
    @staticmethod
    def _insert_submission(
        cursor,
        plan: SubmissionPersistencePlan) -> int:
        submission = plan.submission
        cursor.execute(
            """
            INSERT INTO dbo.SUBMISSION (
                batch_id,
                relation_id,
                external_supplier_key,
                respondent_id,
                respondent_mp_id,
                org_size,
                submitted_at,
                status,
                raw_payload,
                created_at,
                updated_at
            )
            OUTPUT INSERTED.submission_id
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            )
            """,
            submission.batch_id,
            submission.relation_id,
            submission.external_supplier_key,
            submission.respondent_id,
            submission.respondent_mp_id,
            submission.org_size,
            submission.submitted_at,
            submission.status,
            submission.raw_payload,
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(
                "SUBMISSION insert did not "
                "return submission_id"
            )

        return int(row[0])

    @staticmethod
    def _insert_submission_answer(
        cursor,
        submission_id: int,
        question_id: str,
    ) -> int:
        cursor.execute(
            """
            INSERT INTO dbo.SUBMISSION_ANSWER (
                submission_id,
                question_id
            )
            OUTPUT INSERTED.submission_answer_id
            VALUES (?, ?)
            """,
            submission_id,
            question_id,
        )

        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "SUBMISSION_ANSWER insert did not "
                "return submission_answer_id"
            )

        return int(row[0])

    @staticmethod
    def _insert_answer_value(
        cursor,
        submission_answer_id: int,
        value,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO dbo.ANSWER_VALUE (
                submission_answer_id,
                option_id,
                field_type,
                selected,
                number_value,
                text_value
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            submission_answer_id,
            value.option_id,
            value.field_type,
            value.selected,
            value.number_value,
            value.text_value,
        )