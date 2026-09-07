from decimal import Decimal

from alex.esg.domain.answer import Answer
from alex.esg.domain.answer_value import AnswerValue
from alex.esg.domain.submission import Submission
from alex.esg.repositories.mssql_question_definition_repository import MssqlQuestionDefinitionRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

class MssqlSubmissionAnswerLoader:
    def __init__(
        self,
        connection_factory: SqlServerConnectionFactory,
        question_definition_repository: (MssqlQuestionDefinitionRepository),
    ) -> None:
        if not isinstance(
            connection_factory,
            SqlServerConnectionFactory,
        ):
            raise TypeError(
                "connection_factory must be a "
                "SqlServerConnectionFactory"
            )
        if not isinstance(
            question_definition_repository,
            MssqlQuestionDefinitionRepository,
        ):
            raise TypeError(
                "question_definition_repository must "
                "be an "
                "MssqlQuestionDefinitionRepository"
            )
        self._connection_factory = (connection_factory)
        self._question_definition_repository = (question_definition_repository)

    def load(
        self,
        submission: Submission,
    ) -> Submission:
        if not isinstance(
            submission,
            Submission,
        ):
            raise TypeError("submission must be a Submission")
        definitions = (self._question_definition_repository.list_for_questionnaire(submission.questionnaire))
        definitions_by_id = {
            definition.question.question_id:
                definition
            for definition in definitions
        }
        rows = self._load_rows(submission.submission_id)
        grouped: dict[
            int | str,
            dict,
        ] = {}

        for row in rows:
            submission_answer_id = row[0]
            question_id = row[1]
            if (
                question_id not in definitions_by_id
            ):
                raise ValueError("question definition not found: " f"{question_id}")

            if (
                submission_answer_id  not in grouped
            ):
                grouped[
                    submission_answer_id
                ] = {
                    "question_id": (question_id),
                    "values": [],
                }
            answer_value_id = row[2]
            if answer_value_id is None:
                continue

            value = AnswerValue(
                field_type=(self._normalize_field_type(row[4])),
                option_id=(self._normalize_option_id(row[3])),
                selected=(self._normalize_selected(row[5])),
                number_value=(self._normalize_number(row[6])),
                text_value=(row[7]),
            )

            grouped[submission_answer_id]["values"].append(value)
        for data in grouped.values():
            question_id = (data["question_id"])
            definition = (definitions_by_id[question_id])
            answer = Answer(
                submission=submission,
                question_definition=definition,
                values=data["values"],
            )

            submission.add_answer(
                answer,
                touch_updated_at=False,
            )

        return submission

    def _load_rows(
        self,
        submission_id: str,
    ):
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    sa.submission_answer_id,
                    sa.question_id,

                    av.answer_value_id,
                    av.option_id,
                    av.field_type,
                    av.selected,
                    av.number_value,
                    av.text_value

                FROM dbo.SUBMISSION_ANSWER sa

                LEFT JOIN dbo.ANSWER_VALUE av
                    ON av.submission_answer_id =
                       sa.submission_answer_id

                WHERE
                    sa.submission_id =
                    TRY_CONVERT(bigint, ?)

                ORDER BY
                    sa.submission_answer_id,
                    av.answer_value_id
                """,
                submission_id,
            )
            return cursor.fetchall()
        finally:
            connection.close()

    @staticmethod
    def _normalize_field_type(
        value,
    ) -> str:
        if value is None:
            raise ValueError("answer field_type is missing")
        normalized = (str(value).strip().lower())
        if not normalized:
            raise ValueError("answer field_type is empty")
        return normalized

    @staticmethod
    def _normalize_option_id(
        value,
    ) -> str | None:
        if value is None:
            return None
        normalized = (str(value).strip())
        return (normalized or None)

    @staticmethod
    def _normalize_selected(
        value,
    ) -> bool | None:
        if value is None:
            return None
        return bool(value)

    @staticmethod
    def _normalize_number(
        value,
    ) -> int | float | None:
        if value is None:
            return None
        if isinstance(
            value,
            Decimal,
        ):
            if (
                value  == value.to_integral_value()
            ):
                return int(value)
            return float(value)
        if isinstance(value, bool):
            raise TypeError("number_value cannot be bool")
        if isinstance(
            value,
            (int, float),
        ):
            return value
        raise TypeError("unsupported number_value type: " f"{type(value).__name__}")