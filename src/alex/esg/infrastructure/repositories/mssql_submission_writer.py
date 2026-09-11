from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceData
from collections import Counter

@dataclass(frozen=True)
class MssqlSubmissionSupplementPreflightResult:
    existing_submission_id: int | None

    supplement_answers: tuple[
        SubmissionAnswerPersistenceData,
        ...
    ]

    @property
    def is_supplement(self) -> bool:
        return (
            self.existing_submission_id is not None
            and bool(self.supplement_answers)
        )

    @property
    def answer_count(self) -> int:
        return len(
            self.supplement_answers
        )

    @property
    def answer_value_count(self) -> int:
        return sum(
            len(answer.values)
            for answer
            in self.supplement_answers
        )

@dataclass(frozen=True)
class MssqlSubmissionWriteResult:
    submission_id: int
    created: bool
    answer_count: int
    answer_value_count: int

@dataclass(frozen=True)
class MssqlSubmissionSupplementResult:
    submission_id: int
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

    def preflight_supplement(
        self,
        plan: SubmissionPersistencePlan,
    ) -> (
        MssqlSubmissionSupplementPreflightResult
    ):
        if not isinstance(
            plan,
            SubmissionPersistencePlan,
        ):
            raise TypeError("plan must be a SubmissionPersistencePlan")
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            self._ensure_batch_exists(
                cursor,
                plan.submission.batch_id,
            )
            result = (self._preflight_supplement_read_only(
                    cursor,
                    plan,
                )
            )

            connection.rollback()
            return result

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

    def supplement_answers(
        self,
        submission_id: int,
        answers: tuple[
            SubmissionAnswerPersistenceData,
            ...
        ],
    ) -> MssqlSubmissionSupplementResult:
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            result = (
                self.supplement_answers_on_cursor(
                    cursor,
                    submission_id,
                    answers,
                )
            )

            connection.commit()

            return result

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def supplement_answers_on_cursor(
        self,
        cursor,
        submission_id: int,
        answers: tuple[
            SubmissionAnswerPersistenceData,
            ...
        ],
    ) -> MssqlSubmissionSupplementResult:
        if (
            not isinstance(
                submission_id,
                int,
            )
            or isinstance(
                submission_id,
                bool,
            )
        ):
            raise TypeError("submission_id must be an integer")

        if submission_id <= 0:
            raise ValueError("submission_id must be positive")

        if not isinstance(
            answers,
            tuple,
        ):
            raise TypeError("answers must be a tuple")

        for answer in answers:
            if not isinstance(
                answer,
                SubmissionAnswerPersistenceData,
            ):
                raise TypeError("all answers must be SubmissionAnswerPersistenceData")

        self._ensure_submission_exists_for_write(
            cursor,
            submission_id,
        )

        existing_question_ids = (
            self._find_existing_question_ids_for_write(
                cursor,
                submission_id,
            )
        )

        seen_question_ids = set()
        for answer in answers:
            question_id = (answer.question_id)

            if question_id in seen_question_ids:
                raise ValueError(
                    "duplicate question_id in supplement: "
                    f"{question_id}"
                )

            seen_question_ids.add(question_id)

            if (question_id in existing_question_ids
            ):
                raise ValueError(
                    "SUBMISSION_ANSWER already "
                    "exists for submission: "
                    f"{submission_id}, "
                    f"question_id={question_id}"
                )

        answer_count = 0
        answer_value_count = 0

        for answer in answers:
            submission_answer_id = (self._insert_submission_answer(
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

        return (MssqlSubmissionSupplementResult(
                submission_id=submission_id,
                answer_count=answer_count,
                answer_value_count=(answer_value_count),
            )
        )

    @staticmethod
    def _ensure_submission_exists_for_write(
        cursor,
        submission_id: int,
    ) -> None:
        cursor.execute(
            """
            SELECT
                submission_id
            FROM dbo.SUBMISSION
                WITH (UPDLOCK, HOLDLOCK)
            WHERE submission_id = ?
            """,
            submission_id,
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                "SUBMISSION does not exist: "
                f"{submission_id}"
            )

    @staticmethod
    def _find_existing_question_ids_for_write(
        cursor,
        submission_id: int,
    ) -> set[str]:
        cursor.execute(
            """
            SELECT
                question_id
            FROM dbo.SUBMISSION_ANSWER
                WITH (UPDLOCK, HOLDLOCK)
            WHERE submission_id = ?
            """,
            submission_id,
        )

        return {str(row[0]).strip() for row in cursor.fetchall()}

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

        normalized_period = "".join(character for character in period if character.isalnum()
        )

        return ( f"RESP_{normalized_identifier}_" f"{normalized_period}" )
    @classmethod
    def _split_respondent_id_for_match(
        cls,
        value,
    ) -> tuple[
        str,
        str,
    ] | None:
        normalized = (cls._normalize_respondent_id_for_match(value))
        if not normalized.startswith("RESP_"
        ):
            return None
        body = normalized[5:]
        identifier, separator, period = (body.rpartition("_"))
        if not separator:
            return None
        return (
            identifier,
            period,
        )
    @classmethod
    def _preflight_supplement_read_only(
        cls,
        cursor,
        plan: SubmissionPersistencePlan,
    ) -> ( MssqlSubmissionSupplementPreflightResult
    ):
        submission = plan.submission
        planned_parts = (cls._split_respondent_id_for_match(submission.respondent_id))

        if planned_parts is None:
            return (MssqlSubmissionSupplementPreflightResult(
                    existing_submission_id=None,
                    supplement_answers=(),
                )
            )

        (
            planned_identifier,
            planned_period,
        ) = planned_parts


        if planned_period == "NOPERIOD":
            return (
                MssqlSubmissionSupplementPreflightResult(
                    existing_submission_id=None,
                    supplement_answers=(),
                )
            )

        cursor.execute(
            """
            SELECT
                submission_id,
                respondent_id,
                external_supplier_key,
                respondent_mp_id,
                submitted_at
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

        matching_candidates = []

        for row in cursor.fetchall():
            candidate_id = int(row[0])
            candidate_respondent_id = (row[1])
            candidate_supplier_key = (None if row[2] is None else str(row[2]).strip())
            candidate_submitted_at = (row[4])
            candidate_parts = (cls._split_respondent_id_for_match(candidate_respondent_id))

            if candidate_parts is None:
                continue
            (
                candidate_identifier,
                candidate_period,
            ) = candidate_parts
            if (
                candidate_identifier
                != planned_identifier
            ):
                continue
            if candidate_period != "NOPERIOD":
                continue
            if (
                candidate_supplier_key != submission.external_supplier_key
            ):
                continue

            if (
                candidate_submitted_at != submission.submitted_at
            ):
                continue
            matching_candidates.append( candidate_id)
        if not matching_candidates:
            return (
                MssqlSubmissionSupplementPreflightResult(
                    existing_submission_id=None,
                    supplement_answers=(),
                )
            )
        if len(matching_candidates) != 1:
            raise ValueError(
                "multiple legacy supplement "
                "submission candidates: "
                f"{matching_candidates}"
            )
        existing_submission_id = (matching_candidates[0])
        cursor.execute(
            """
            SELECT
                sa.question_id,
                av.field_type,
                av.option_id,
                av.selected,
                av.number_value,
                av.text_value
            FROM dbo.SUBMISSION_ANSWER AS sa

            LEFT JOIN dbo.ANSWER_VALUE AS av
                ON av.submission_answer_id =
                   sa.submission_answer_id

            WHERE sa.submission_id = ?

            ORDER BY
                sa.question_id,
                sa.submission_answer_id,
                av.answer_value_id
            """,
            existing_submission_id,
        )

        db_values_by_question = {}

        for row in cursor.fetchall():
            question_id = str(row[0]).strip()
            db_values_by_question.setdefault(
                question_id,
                [],
            )
            if row[1] is None:
                continue

            db_values_by_question[question_id].append(
                cls._answer_value_key(
                    field_type=row[1],
                    option_id=row[2],
                    selected=row[3],
                    number_value=row[4],
                    text_value=row[5],
                )
            )

        plan_answers_by_question = {answer.question_id: answer for answer in plan.answers}
        db_question_ids = set(db_values_by_question)
        plan_question_ids = set(plan_answers_by_question)
        only_in_db = (db_question_ids - plan_question_ids)
        if only_in_db:
            raise ValueError("legacy submission contains question(s) missing from plan: "+ ", ".join(sorted(only_in_db)))

        common_question_ids = (db_question_ids & plan_question_ids)

        for question_id in sorted(common_question_ids
        ):
            db_values = Counter(db_values_by_question[question_id])
            answer = (plan_answers_by_question[ question_id])

            plan_values = Counter(cls._answer_value_key(
                    field_type=value.field_type,
                    option_id=value.option_id,
                    selected=value.selected,
                    number_value=value.number_value,
                    text_value=value.text_value,
                )
                for value in answer.values
            )

            if db_values != plan_values:
                raise ValueError(
                    "legacy submission answer differs from plan: " f"{question_id}")

        missing_question_ids = (plan_question_ids- db_question_ids)

        if not missing_question_ids:
            return (MssqlSubmissionSupplementPreflightResult(
                    existing_submission_id=(existing_submission_id),
                    supplement_answers=(),
                )
            )

        supplement_answers = tuple(answer for answer in plan.answers
            if (
                answer.question_id in missing_question_ids
            )
        )

        return (
            MssqlSubmissionSupplementPreflightResult(
                existing_submission_id=(existing_submission_id),
                supplement_answers=(supplement_answers),
            )
        )

    @staticmethod
    def _answer_value_key(
        *,
        field_type,
        option_id,
        selected,
        number_value,
        text_value,
    ) -> tuple:
        normalized_field_type = (None if field_type is None else str(field_type).strip())
        normalized_option_id = (None if option_id is None else str(option_id).strip())
        normalized_selected = (None if selected is None else bool(selected))

        return (
            normalized_field_type,
            normalized_option_id,
            normalized_selected,
            number_value,
            text_value,
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

            actual = (cls._normalize_respondent_id_for_match(row[1]))
            if actual == expected:matching_submission_ids.append(int(row[0]))

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