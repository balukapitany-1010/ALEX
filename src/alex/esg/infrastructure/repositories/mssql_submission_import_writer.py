from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan

@dataclass(frozen=True)
class MssqlSubmissionImportWriteResult:
    batch_result: object
    submission_results: tuple

    @property
    def batch_created(self) -> bool:
        return self.batch_result.created

    @property
    def created_submission_count(self) -> int:
        return sum(1 for result in self.submission_results if result.created)

    @property
    def existing_submission_count(self) -> int:
        return sum(1 for result in self.submission_results if not result.created)

    @property
    def created_answer_count(self) -> int:
        return sum(result.answer_count for result in self.submission_results if result.created)

    @property
    def created_answer_value_count(self) -> int:
        return sum(result.answer_value_count for result in self.submission_results if result.created)

class MssqlSubmissionImportWriter:
    def __init__(
        self,
        *,
        connection_factory,
        batch_writer,
        submission_writer,
    ) -> None:
        self._connection_factory = (connection_factory)
        self._batch_writer = (batch_writer)
        self._submission_writer = (submission_writer)

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

    def _write_on_cursor(
            self,
            cursor,
            *,
            batch_id: str,
            questionnaire_code: str,
            spec_version: str,
            plans: list[
                SubmissionPersistencePlan
            ],
    ) -> MssqlSubmissionImportWriteResult:
        batch_result = (
            self._batch_writer
            .ensure_batch_on_cursor(
                cursor,
                batch_id=batch_id,
                questionnaire_code=(
                    questionnaire_code
                ),
                spec_version=spec_version,
            )
        )

        submission_results = (
            self._submission_writer
            .write_many_on_cursor(
                cursor,
                plans,
            )
        )

        return MssqlSubmissionImportWriteResult(
            batch_result=batch_result,
            submission_results=(
                submission_results
            ),
        )

    def write(
        self,
        *,
        batch_id: str,
        questionnaire_code: str,
        spec_version: str,
        plans: list[SubmissionPersistencePlan],
    ) -> MssqlSubmissionImportWriteResult:
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
        spec_version = (
            self._required_text(
                spec_version,
                "spec_version",
            )
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
            if (
                plan.submission.batch_id != batch_id
            ):
                raise ValueError("plan batch_id does not match import batch_id")

        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()

            result = self._write_on_cursor(
                cursor,
                batch_id=batch_id,
                questionnaire_code=(
                    questionnaire_code
                ),
                spec_version=spec_version,
                plans=plans,
            )

            connection.commit()

            return result

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def write_rollback(
            self,
            *,
            batch_id: str,
            questionnaire_code: str,
            spec_version: str,
            plans: list[
                SubmissionPersistencePlan
            ],
    ) -> MssqlSubmissionImportWriteResult:
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

        spec_version = (
            self._required_text(
                spec_version,
                "spec_version",
            )
        )

        if not isinstance(
                plans,
                list,
        ):
            raise TypeError(
                "plans must be a list"
            )

        if not plans:
            raise ValueError(
                "plans cannot be empty"
            )

        for plan in plans:
            if not isinstance(
                    plan,
                    SubmissionPersistencePlan,
            ):
                raise TypeError(
                    "all plans must be "
                    "SubmissionPersistencePlan"
                )

            if (
                    plan.submission.batch_id
                    != batch_id
            ):
                raise ValueError(
                    "plan batch_id does not "
                    "match import batch_id"
                )

        connection = (
            self._connection_factory.connect()
        )

        try:
            cursor = connection.cursor()

            result = self._write_on_cursor(
                cursor,
                batch_id=batch_id,
                questionnaire_code=(
                    questionnaire_code
                ),
                spec_version=spec_version,
                plans=plans,
            )

            # Szándékosan nincs COMMIT.
            connection.rollback()

            return result

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()