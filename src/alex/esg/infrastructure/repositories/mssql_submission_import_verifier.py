from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan


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
                raise TypeError("all plans must be SubmissionPersistencePlan"
                )

            if (
                plan.submission.batch_id != batch_id
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