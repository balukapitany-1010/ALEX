from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan
from collections import Counter

@dataclass(frozen=True)
class MssqlSubmissionSupplementVerificationRequest:
    submission_id: int
    plan: SubmissionPersistencePlan


@dataclass(frozen=True)
class MssqlSubmissionSupplementVerificationItemResult:
    submission_id: int

    submission_exists: bool
    parent_matches: bool

    expected_answer_count: int
    actual_answer_count: int

    expected_answer_value_count: int
    actual_answer_value_count: int

    question_ids_match: bool
    answer_values_match: bool

    @property
    def answer_count_matches(self) -> bool:
        return (
            self.expected_answer_count
            == self.actual_answer_count
        )

    @property
    def answer_value_count_matches(self) -> bool:
        return (
            self.expected_answer_value_count
            == self.actual_answer_value_count
        )

    @property
    def is_valid(self) -> bool:
        return all(
            (
                self.submission_exists,
                self.parent_matches,
                self.answer_count_matches,
                self.answer_value_count_matches,
                self.question_ids_match,
                self.answer_values_match,
            )
        )


@dataclass(frozen=True)
class MssqlSubmissionSupplementVerificationResult:
    items: tuple[
        MssqlSubmissionSupplementVerificationItemResult,
        ...
    ]

    @property
    def submission_count(self) -> int:
        return len(self.items)

    @property
    def expected_answer_count(self) -> int:
        return sum(item.expected_answer_count for item in self.items)

    @property
    def actual_answer_count(self) -> int:
        return sum(item.actual_answer_count for item in self.items)

    @property
    def expected_answer_value_count(self) -> int:
        return sum(item.expected_answer_value_count  for item in self.items)

    @property
    def actual_answer_value_count(self) -> int:
        return sum(item.actual_answer_value_count for item in self.items)

    @property
    def is_valid(self) -> bool:
        return all(item.is_valid for item in self.items)

@dataclass(frozen=True)
class MssqlSubmissionWriteVerificationRequest:
    submission_id: int
    plan: SubmissionPersistencePlan

@dataclass(frozen=True)
class MssqlSubmissionImportVerificationResult:
    batch_id: str

    questionnaire_code: str
    spec_version: str

    batch_exists: bool
    questionnaire_matches: bool

    expected_submission_count: int
    actual_submission_count: int

    expected_answer_count: int
    actual_answer_count: int

    expected_answer_value_count: int
    actual_answer_value_count: int

    @property
    def submission_count_matches(
        self,
    ) -> bool:
        return (self.expected_submission_count == self.actual_submission_count)

    @property
    def answer_count_matches(
        self,
    ) -> bool:
        return (self.expected_answer_count == self.actual_answer_count)

    @property
    def answer_value_count_matches(
        self,
    ) -> bool:
        return (self.expected_answer_value_count == self.actual_answer_value_count)

    @property
    def is_valid(
        self,
    ) -> bool:
        return all(
            (
                self.batch_exists,
                self.questionnaire_matches,
                self.submission_count_matches,
                self.answer_count_matches,
                self.answer_value_count_matches,
            )
        )


class MssqlSubmissionImportVerifier:
    def __init__(
        self,
        connection_factory,
    ) -> None:
        self._connection_factory = (connection_factory)

    @staticmethod
    def _required_text(
        value,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(f"{field_name} cannot be empty")
        text = str(value).strip()

        if not text:
            raise ValueError(f"{field_name} cannot be empty")

        return text
    @staticmethod
    def _optional_text(
        value,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        return text or None

    @staticmethod
    def _answer_value_key(
        *,
        field_type,
        option_id,
        selected,
        number_value,
        text_value,
    ) -> tuple:
        return (
            (None if field_type is None else str(field_type).strip()),
            (None if option_id is None else str(option_id).strip()),
            (None if selected is None else bool(selected)),
            number_value,
            text_value,
        )

    @staticmethod
    def _validate_supplement_requests(
        requests: list[MssqlSubmissionSupplementVerificationRequest],
    ) -> None:
        if not isinstance(
            requests,
            list,
        ):
            raise TypeError("requests must be a list")

        if not requests:
            raise ValueError("requests cannot be empty")

        seen_submission_ids = set()

        for request in requests:
            if not isinstance(
                request,
                MssqlSubmissionSupplementVerificationRequest,
            ):
                raise TypeError("all requests must be MssqlSubmissionSupplementVerificationRequest")

            if (
                not isinstance(
                    request.submission_id,
                    int,
                )
                or isinstance(
                    request.submission_id,
                    bool,
                )
            ):
                raise TypeError("submission_id must be an integer")

            if request.submission_id <= 0:
                raise ValueError("submission_id must be positive")

            if (request.submission_id in seen_submission_ids
            ):
                raise ValueError(
                    "duplicate verification submission_id: "
                    f"{request.submission_id}"
                )

            seen_submission_ids.add(request.submission_id)

            if not isinstance(
                request.plan,
                SubmissionPersistencePlan,
            ):
                raise TypeError("plan must be a SubmissionPersistencePlan")

    def verify_supplement_items(
        self,
        *,
        items: list,
    ) -> (MssqlSubmissionSupplementVerificationResult
    ):
        if not isinstance(
            items,
            list,
        ):
            raise TypeError("items must be a list")
        if not items:
            raise ValueError("items cannot be empty")
        requests = []
        for item in items:
            if not getattr(
                item,
                "is_supplement",
                False,
            ):
                raise ValueError("all items must be supplement items")
            if (item.existing_submission_id is None
            ):
                raise ValueError("supplement item must have existing_submission_id")
            if item.plan is None:
                raise ValueError("supplement item must have persistence plan")
            requests.append(MssqlSubmissionSupplementVerificationRequest(
                    submission_id=(item.existing_submission_id),
                    plan=item.plan,
                )
            )
        return self.verify_supplements(requests=requests)

    def verify_written_results(
        self,
        *,
        plans: list[SubmissionPersistencePlan],
        write_results: tuple,
    ) -> (MssqlSubmissionSupplementVerificationResult
    ):
        if not isinstance(
            plans,
            list,
        ):
            raise TypeError("plans must be a list")

        if not isinstance(
            write_results,
            tuple,
        ):
            raise TypeError("write_results must be a tuple")
        if len(plans) != len(write_results):
            raise ValueError("plans and write_results count must match")
        requests = []
        for plan, write_result in zip(
            plans,
            write_results,
            strict=True,
        ):
            if not isinstance(
                plan,
                SubmissionPersistencePlan,
            ):
                raise TypeError("all plans must be SubmissionPersistencePlan")

            created = getattr(
                write_result,
                "created",
                None,
            )

            if not isinstance(
                created,
                bool,
            ):
                raise TypeError("write result created must be a bool")

            if not created:
                continue

            submission_id = getattr(
                write_result,
                "submission_id",
                None,
            )

            requests.append(MssqlSubmissionWriteVerificationRequest(
                    submission_id=submission_id,
                    plan=plan,
                )
            )
        if not requests:
            raise ValueError("no created submissions to verify")

        return self.verify_written_submissions(requests=requests)

    def verify_written_submissions(
        self,
        *,
        requests: list[MssqlSubmissionWriteVerificationRequest],
    ) -> (MssqlSubmissionSupplementVerificationResult
    ):
        if not isinstance(
            requests,
            list,
        ):
            raise TypeError("requests must be a list")
        if not requests:
            raise ValueError("requests cannot be empty")
        seen_submission_ids = set()
        for request in requests:
            if not isinstance(
                request,
                MssqlSubmissionWriteVerificationRequest,
            ):
                raise TypeError("all requests must be MssqlSubmissionWriteVerificationRequest")

            if (
                not isinstance(
                    request.submission_id,
                    int,
                )
                or isinstance(
                    request.submission_id,
                    bool,
                )
            ):
                raise TypeError("submission_id must be an integer")
            if request.submission_id <= 0:
                raise ValueError("submission_id must be positive")

            if (request.submission_id in seen_submission_ids
            ):
                raise ValueError("duplicate verification submission_id: "f"{request.submission_id}")

            seen_submission_ids.add(request.submission_id)
            if not isinstance(
                request.plan,
                SubmissionPersistencePlan,
            ):
                raise TypeError("plan must be a SubmissionPersistencePlan")
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()
            results = []
            for request in requests:
                submission_id = (request.submission_id)
                plan = request.plan
                submission = plan.submission
                cursor.execute(
                    """
                    SELECT
                        batch_id,
                        relation_id,
                        external_supplier_key,
                        respondent_id,
                        respondent_mp_id,
                        org_size,
                        submitted_at,
                        status
                    FROM dbo.SUBMISSION
                    WHERE submission_id = ?
                    """,
                    submission_id,
                )
                parent_row = cursor.fetchone()
                if parent_row is None:
                    results.append(MssqlSubmissionSupplementVerificationItemResult(
                            submission_id=submission_id,
                            submission_exists=False,
                            parent_matches=False,
                            expected_answer_count=(plan.answer_count),
                            actual_answer_count=0,
                            expected_answer_value_count=(plan.answer_value_count),
                            actual_answer_value_count=0,
                            question_ids_match=False,
                            answer_values_match=False,
                        )
                    )
                    continue
                parent_matches = all(
                    (
                        (str(parent_row[0]).strip() == submission.batch_id),
                        (int(parent_row[1]) == submission.relation_id),
                        (self._optional_text(parent_row[2]) == self._optional_text(submission.external_supplier_key)),
                        (self._optional_text(parent_row[3]) == self._optional_text(submission.respondent_id)),
                        (self._optional_text(parent_row[4]) == self._optional_text(submission.respondent_mp_id)),
                        (self._optional_text(parent_row[5]) == self._optional_text(submission.org_size)),
                        (parent_row[6] == submission.submitted_at),
                        (self._optional_text(parent_row[7]) == self._optional_text(submission.status)),
                    )
                )

                cursor.execute(
                    """
                    SELECT
                        sa.submission_answer_id,
                        sa.question_id,
                        av.field_type,
                        av.option_id,
                        av.selected,
                        av.number_value,
                        av.text_value
                    FROM dbo.SUBMISSION_ANSWER AS sa

                    LEFT JOIN dbo.ANSWER_VALUE AS av
                        ON av.submission_answer_id
                         = sa.submission_answer_id

                    WHERE sa.submission_id = ?

                    ORDER BY
                        sa.question_id,
                        sa.submission_answer_id,
                        av.answer_value_id
                    """,
                    submission_id,
                )
                actual_answer_ids = set()
                actual_values_by_question = {}
                for row in cursor.fetchall():
                    submission_answer_id = int(row[0])
                    question_id = str(row[1]).strip()
                    actual_answer_ids.add(submission_answer_id)
                    actual_values_by_question.setdefault(question_id,[],)
                    if row[2] is None:
                        continue
                    actual_values_by_question[question_id].append(self._answer_value_key(
                            field_type=row[2],
                            option_id=row[3],
                            selected=row[4],
                            number_value=row[5],
                            text_value=row[6],
                        )
                    )
                plan_values_by_question = {}
                for answer in plan.answers:
                    if (answer.question_id in plan_values_by_question
                    ):
                        raise ValueError("duplicate question_id in verification plan: "
                            f"{answer.question_id}"
                        )
                    plan_values_by_question[answer.question_id] = [
                        self._answer_value_key(
                            field_type=value.field_type,
                            option_id=value.option_id,
                            selected=value.selected,
                            number_value=value.number_value,
                            text_value=value.text_value,
                        )
                        for value in answer.values
                    ]
                actual_question_ids = set(actual_values_by_question)
                expected_question_ids = set(plan_values_by_question)
                question_ids_match = (actual_question_ids == expected_question_ids)
                answer_values_match = (question_ids_match)
                if answer_values_match:
                    for question_id in sorted(expected_question_ids
                    ):
                        if (Counter(actual_values_by_question[question_id]) != Counter(plan_values_by_question[question_id])
                        ):
                            answer_values_match = False
                            break
                actual_answer_count = len(actual_answer_ids)
                actual_answer_value_count = sum(len(values) for values in actual_values_by_question.values())
                results.append(MssqlSubmissionSupplementVerificationItemResult(
                        submission_id=submission_id,
                        submission_exists=True,
                        parent_matches=parent_matches,
                        expected_answer_count=(plan.answer_count),
                        actual_answer_count=(actual_answer_count),
                        expected_answer_value_count=(plan.answer_value_count),
                        actual_answer_value_count=(actual_answer_value_count),
                        question_ids_match=(question_ids_match),
                        answer_values_match=(answer_values_match),
                    )
                )
            return (MssqlSubmissionSupplementVerificationResult(items=tuple(results),))
        finally:
            try:
                connection.rollback()
            finally:
                connection.close()

    def verify_supplements(
        self,
        *,
        requests: list[MssqlSubmissionSupplementVerificationRequest],
    ) -> (
        MssqlSubmissionSupplementVerificationResult
    ):
        self._validate_supplement_requests(requests)
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            results = []
            for request in requests:
                submission_id = (request.submission_id)
                plan = request.plan
                submission = plan.submission

                cursor.execute(
                    """
                    SELECT
                        batch_id,
                        relation_id,
                        external_supplier_key,
                        respondent_mp_id,
                        submitted_at
                    FROM dbo.SUBMISSION
                    WHERE submission_id = ?
                    """,
                    submission_id,
                )

                parent_row = cursor.fetchone()

                if parent_row is None:
                    results.append(MssqlSubmissionSupplementVerificationItemResult(
                            submission_id=(submission_id),
                            submission_exists=False,
                            parent_matches=False,
                            expected_answer_count=(plan.answer_count),
                            actual_answer_count=0,
                            expected_answer_value_count=(plan.answer_value_count),
                            actual_answer_value_count=0,
                            question_ids_match=False,
                            answer_values_match=False,
                        )
                    )
                    continue

                parent_matches = all(
                    (
                        (
                                str( parent_row[0]).strip() == submission.batch_id
                        ),
                        (
                                int(parent_row[1])  == submission.relation_id
                        ),
                        (
                                self._optional_text(parent_row[2])  == self._optional_text(submission.external_supplier_key
                        )
                        ),
                        (
                                self._optional_text(parent_row[3]) == self._optional_text(submission.respondent_mp_id
                        )
                        ),
                        (
                                parent_row[4] == submission.submitted_at
                        ),
                    )
                )

                cursor.execute(
                    """
                    SELECT
                        sa.submission_answer_id,
                        sa.question_id,
                        av.field_type,
                        av.option_id,
                        av.selected,
                        av.number_value,
                        av.text_value
                    FROM dbo.SUBMISSION_ANSWER AS sa

                    LEFT JOIN dbo.ANSWER_VALUE AS av
                        ON av.submission_answer_id
                         = sa.submission_answer_id

                    WHERE sa.submission_id = ?

                    ORDER BY
                        sa.question_id,
                        sa.submission_answer_id,
                        av.answer_value_id
                    """,
                    submission_id,
                )

                actual_answer_ids = set()
                actual_values_by_question = {}
                for row in cursor.fetchall():
                    submission_answer_id = int(row[0])
                    question_id = str(row[1]).strip()
                    actual_answer_ids.add(submission_answer_id)
                    actual_values_by_question.setdefault(
                        question_id,
                        [],
                    )

                    if row[2] is None:
                        continue

                    actual_values_by_question[question_id].append(self._answer_value_key(
                            field_type=row[2],
                            option_id=row[3],
                            selected=row[4],
                            number_value=row[5],
                            text_value=row[6],
                        )
                    )
                plan_values_by_question = {}
                for answer in plan.answers:
                    if (
                            answer.question_id in plan_values_by_question
                    ):
                        raise ValueError(
                            "duplicate question_id in verification plan: "
                            f"{answer.question_id}"
                        )
                    plan_values_by_question[answer.question_id] = [self._answer_value_key(
                            field_type=(value.field_type),
                            option_id=(value.option_id),
                            selected=(value.selected),
                            number_value=(value.number_value),
                            text_value=(value.text_value),
                        )
                        for value in answer.values]

                actual_question_ids = set(actual_values_by_question)
                expected_question_ids = set(plan_values_by_question)
                question_ids_match = (actual_question_ids == expected_question_ids)
                answer_values_match = (question_ids_match)
                if answer_values_match:
                    for question_id in sorted(expected_question_ids
                    ):
                        if (
                                Counter(actual_values_by_question[question_id]) != Counter(plan_values_by_question[question_id]
                        )
                        ):
                            answer_values_match = False
                            break
                actual_answer_count = len(actual_answer_ids)
                actual_answer_value_count = sum(len(values) for values in actual_values_by_question.values())
                results.append(MssqlSubmissionSupplementVerificationItemResult(
                        submission_id=(submission_id),
                        submission_exists=True,
                        parent_matches=(parent_matches),
                        expected_answer_count=(plan.answer_count),
                        actual_answer_count=(actual_answer_count),
                        expected_answer_value_count=(plan.answer_value_count),
                        actual_answer_value_count=(actual_answer_value_count),
                        question_ids_match=(question_ids_match),
                        answer_values_match=(answer_values_match),
                    )
                )
            return (MssqlSubmissionSupplementVerificationResult(items=tuple(results),))
        finally:
            try:
                connection.rollback()
            finally:
                connection.close()

    def verify_new_batch(
        self,
        *,
        batch_id: str,
        questionnaire_code: str,
        spec_version: str,
        plans: list[
            SubmissionPersistencePlan
        ],
    ) -> MssqlSubmissionImportVerificationResult:
        batch_id = self._required_text(
            batch_id,
            "batch_id",
        )
        questionnaire_code = (
            self._required_text(
                questionnaire_code,
                "questionnaire_code",
            )
        )
        spec_version = self._required_text(
            spec_version,
            "spec_version",
        )

        if not isinstance(
            plans,
            list,
        ):
            raise TypeError("plans must be a list")
        if not plans:
            raise ValueError("plans cannot be empty")
        for plan in plans:
            if not isinstance(
                plan,
                SubmissionPersistencePlan,
            ):
                raise TypeError("all plans must be SubmissionPersistencePlan")

            if (plan.submission.batch_id != batch_id
            ):
                raise ValueError("plan batch_id does not match verification batch_id")
        expected_submission_count = len(plans)
        expected_answer_count = sum(plan.answer_count for plan in plans)
        expected_answer_value_count = sum(plan.answer_value_count for plan in plans)
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    questionnaire_code,
                    spec_version
                FROM dbo.SUBMISSION_BATCH
                WHERE batch_id = ?
                """,
                batch_id,
            )

            batch_row = cursor.fetchone()
            if batch_row is None:
                batch_exists = False
                questionnaire_matches = False

            else:
                batch_exists = True
                actual_questionnaire_code = str(batch_row[0]).strip()
                actual_spec_version = str(batch_row[1]).strip()
                questionnaire_matches = (actual_questionnaire_code == questionnaire_code and actual_spec_version == spec_version)

            cursor.execute(
                """
                SELECT
                    COUNT_BIG(*)
                FROM dbo.SUBMISSION
                WHERE batch_id = ?
                """,
                batch_id,
            )
            actual_submission_count = int(cursor.fetchone()[0])
            cursor.execute(
                """
                SELECT
                    COUNT_BIG(*)
                FROM dbo.SUBMISSION_ANSWER AS sa
                INNER JOIN dbo.SUBMISSION AS s
                    ON s.submission_id
                     = sa.submission_id
                WHERE s.batch_id = ?
                """,
                batch_id,
            )
            actual_answer_count = int(cursor.fetchone()[0])
            cursor.execute(
                """
                SELECT
                    COUNT_BIG(*)
                FROM dbo.ANSWER_VALUE AS av
                INNER JOIN dbo.SUBMISSION_ANSWER AS sa
                    ON sa.submission_answer_id
                     = av.submission_answer_id
                INNER JOIN dbo.SUBMISSION AS s
                    ON s.submission_id
                     = sa.submission_id
                WHERE s.batch_id = ?
                """,
                batch_id,
            )

            actual_answer_value_count = int(cursor.fetchone()[0])

            return (MssqlSubmissionImportVerificationResult(
                    batch_id=batch_id,
                    questionnaire_code=(questionnaire_code),
                    spec_version=(spec_version),
                    batch_exists=batch_exists,
                    questionnaire_matches=(questionnaire_matches),
                    expected_submission_count=(expected_submission_count),
                    actual_submission_count=(actual_submission_count),
                    expected_answer_count=(expected_answer_count),
                    actual_answer_count=(actual_answer_count),
                    expected_answer_value_count=(expected_answer_value_count),
                    actual_answer_value_count=(actual_answer_value_count),
                )
            )

        finally:
            try:
                connection.rollback()
            finally:
                connection.close()