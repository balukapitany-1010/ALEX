from alex.esg.domain.option import Option
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

class MssqlQuestionDefinitionRepository:
    def __init__(
        self,
        connection_factory: SqlServerConnectionFactory,
    ) -> None:
        if not isinstance(
            connection_factory,
            SqlServerConnectionFactory,
        ):
            raise TypeError(
                "connection_factory must be a "
                "SqlServerConnectionFactory"
            )

        self._connection_factory = (connection_factory)

    def list_for_questionnaire(
        self,
        questionnaire: Questionnaire,
    ) -> tuple[QuestionDefinition, ...]:
        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError("questionnaire must be a Questionnaire")

        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    q.question_id,
                    q.question_code,
                    q.requirement,
                    q.topic,
                    q.subtopic,
                    q.title,
                    q.category,
                    q.type,

                    qq.sort_order,

                    qo.option_id,
                    qo.text

                FROM dbo.QUESTIONNAIRE_QUESTION qq

                INNER JOIN dbo.QUESTION q
                    ON q.question_id =
                       qq.question_id

                LEFT JOIN dbo.QUESTIONNAIRE_OPTION qno
                    ON qno.questionnaire_code =
                       qq.questionnaire_code
                    AND qno.spec_version =
                        qq.spec_version
                    AND qno.question_id =
                        qq.question_id
                    AND qno.status = 'active'

                LEFT JOIN dbo.QUESTION_OPTION qo
                    ON qo.question_id =
                       qno.question_id
                    AND qo.option_id =
                        qno.option_id

                WHERE
                    qq.questionnaire_code = ?
                    AND qq.spec_version = ?
                    AND qq.status = 'active'

                ORDER BY
                    qq.sort_order,
                    qq.questionnaire_question_id,
                    qno.sort_order,
                    qno.questionnaire_option_id
                """,
                questionnaire.questionnaire_code,
                questionnaire.spec_version,
            )

            rows = cursor.fetchall()

            return self._map_rows(
                questionnaire=questionnaire,
                rows=rows,
            )

        finally:
            connection.close()

    def get_by_question_id(
        self,
        *,
        questionnaire: Questionnaire,
        question_id: str,
    ) -> QuestionDefinition | None:
        if not isinstance(
            question_id,
            str,
        ):
            raise TypeError("question_id must be a string")

        question_id = (question_id.strip())

        if not question_id:
            raise ValueError("question_id cannot be empty")

        definitions = (self.list_for_questionnaire(questionnaire))

        for definition in definitions:
            if (
                definition.question.question_id == question_id
            ):
                return definition

        return None

    def _map_rows(
        self,
        *,
        questionnaire: Questionnaire,
        rows,
    ) -> tuple[QuestionDefinition, ...]:
        grouped: dict[
            str,
            dict,
        ] = {}

        for row in rows:
            question_id = row[0]

            if question_id not in grouped:
                question_code = row[1]

                if (
                        question_code is None
                        or not str(
                    question_code
                ).strip()
                ):
                    raise ValueError(
                        "question_code is missing "
                        f"for question {question_id}"
                    )

                normalized_question_code = (
                    str(
                        question_code
                    ).strip()
                )

                topic = (
                    str(
                        row[3]
                    ).strip()
                    if (
                            row[3] is not None
                            and str(
                        row[3]
                    ).strip()
                    )
                    else "-"
                )

                title = (
                    str(
                        row[5]
                    ).strip()
                    if (
                            row[5] is not None
                            and str(
                        row[5]
                    ).strip()
                    )
                    else normalized_question_code
                )

                grouped[
                    question_id
                ] = {
                    "question_code": (
                        normalized_question_code
                    ),
                    "requirement": row[2],
                    "topic": topic,
                    "subtopic": row[4],
                    "title": title,
                    "category": (
                        self._map_category(
                            row[6]
                        )
                    ),
                    "question_type": (
                        self._map_question_type(
                            row[7]
                        )
                    ),
                    "options": [],
                    "option_ids": set(),
                }

            option_id = row[9]
            option_text = row[10]

            if (
                option_id is not None
                and option_text is not None
                and str(option_text).strip()
            ):
                option_id = str(option_id).strip()

                if (
                    option_id not in grouped[question_id]["option_ids"]
                ):
                    grouped[
                        question_id
                    ]["options"].append(
                        Option(
                            option_id=option_id,
                            label=str(
                                option_text
                            ).strip(),
                        )
                    )

                    grouped[question_id]["option_ids"].add(option_id)

        definitions = []

        for (
            question_id,
            data,
        ) in grouped.items():
            question = Question(
                question_id=question_id,
                question_code=(data["question_code"]),
            )

            options = data["options"]

            definition = (
                QuestionDefinition.rehydrate_from_storage(
                    question=question,
                    questionnaire=questionnaire,
                    title=data["title"],
                    category=data["category"],
                    topic=data["topic"],
                    subtopic=data["subtopic"],
                    requirement=(data["requirement"]),
                    question_type=(
                        data["question_type"]),
                    options=options,
                )
            )

            definitions.append(definition)

        return tuple(definitions)

    @staticmethod
    def _map_category(
        value,
    ) -> QuestionCategory:
        if value is None:
            raise ValueError("question category is missing")

        normalized = str(value).strip().upper()

        try:
            return QuestionCategory(normalized)

        except ValueError as error:
            raise ValueError("unknown question category: " f"{value}") from error

    @staticmethod
    def _map_question_type(
        value,
    ) -> QuestionType:
        if value is None:
            raise ValueError("question type is missing")

        normalized = (
            str(value)
            .strip()
            .lower()
        )

        aliases = {
            "radio": QuestionType.RADIO,
            "radiogroup": QuestionType.RADIO,
            "checkbox": QuestionType.CHECKBOX,
            "dropdown": QuestionType.DROPDOWN,
            "text": QuestionType.TEXT,
            "comment": QuestionType.COMMENT,
            "number": QuestionType.NUMBER,
            "mixed": QuestionType.MIXED,
            "table": QuestionType.TABLE,
        }

        result = aliases.get(
            normalized
        )

        if result is None:
            raise ValueError("unknown question type: " f"{value}")

        return result