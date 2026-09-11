from dataclasses import dataclass
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlan
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceData

@dataclass(frozen=True)
class MssqlSubmissionSupplementWriteRequest:
    submission_id: int
    answers: tuple[
        SubmissionAnswerPersistenceData,
        ...
    ]


@dataclass(frozen=True)
class MssqlSubmissionSupplementImportWriteResult:
    supplement_results: tuple

    @property
    def supplement_submission_count(
        self,
    ) -> int:
        return len(self.supplement_results)

    @property
    def answer_count(
        self,
    ) -> int:
        return sum(result.answer_count for result in self.supplement_results)

    @property
    def answer_value_count(
        self,
    ) -> int:
        return sum(result.answer_value_count for result in self.supplement_results)

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
    def _validate_supplement_requests(
        requests: list[
            MssqlSubmissionSupplementWriteRequest
        ],
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
                MssqlSubmissionSupplementWriteRequest,
            ):
                raise TypeError("all requests must be MssqlSubmissionSupplementWriteRequest")

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
            if (
                request.submission_id
                in seen_submission_ids
            ):
                raise ValueError("duplicate supplement submission_id: "
                    f"{request.submission_id}"
                )
            seen_submission_ids.add(request.submission_id)
            if not isinstance(
                request.answers,
                tuple,
            ):
                raise TypeError("answers must be a tuple")
            if not request.answers:
                raise ValueError("supplement answers cannot be empty")
            for answer in request.answers:
                if not isinstance(
                    answer,
                    SubmissionAnswerPersistenceData,
                ):
                    raise TypeError("all supplement answers must be SubmissionAnswerPersistenceData")

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
            plans: list[SubmissionPersistencePlan],
    ) -> MssqlSubmissionImportWriteResult:
        batch_result = (self._batch_writer.ensure_batch_on_cursor(
                cursor,
                batch_id=batch_id,
                questionnaire_code=(questionnaire_code),
                spec_version=spec_version,
            )
        )
        submission_results = (self._submission_writer.write_many_on_cursor(
                cursor,
                plans,
            )
        )
        return MssqlSubmissionImportWriteResult(
            batch_result=batch_result,
            submission_results=(submission_results),
        )

    def _write_supplements_on_cursor(
        self,
        cursor,
        *,
        requests: list[
            MssqlSubmissionSupplementWriteRequest
        ],
    ) -> (
        MssqlSubmissionSupplementImportWriteResult
    ):
        results = []

        for request in requests:
            result = (self._submission_writer.supplement_answers_on_cursor(
                    cursor,
                    request.submission_id,
                    request.answers,))
            results.append(result)
        return (MssqlSubmissionSupplementImportWriteResult(supplement_results=tuple(results),))

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
                questionnaire_code=(questionnaire_code),
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

    def write_supplement_items(
        self,
        *,
        items: list,
    ) -> (MssqlSubmissionSupplementImportWriteResult
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
            submission_id = (item.existing_submission_id)
            if submission_id is None:
                raise ValueError("supplement item must have existing_submission_id")
            requests.append(MssqlSubmissionSupplementWriteRequest(
                    submission_id=(submission_id),
                    answers=(item.supplement_answers),
                )
            )
        return self.write_supplements(requests=requests)

    def write_supplements(
        self,
        *,
        requests: list[MssqlSubmissionSupplementWriteRequest],
    ) -> (MssqlSubmissionSupplementImportWriteResult
    ):
        self._validate_supplement_requests(requests)
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            result = ( self._write_supplements_on_cursor(
                    cursor,
                    requests=requests,
                )
            )
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def write_supplements_rollback(
        self,
        *,
        requests: list[MssqlSubmissionSupplementWriteRequest],
    ) -> (MssqlSubmissionSupplementImportWriteResult
    ):
        self._validate_supplement_requests(requests)
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()
            result = (self._write_supplements_on_cursor(
                    cursor,
                    requests=requests,
                )
            )
            connection.rollback()
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
                questionnaire_code=(questionnaire_code),
                spec_version=spec_version,
                plans=plans,
            )
            connection.rollback()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()