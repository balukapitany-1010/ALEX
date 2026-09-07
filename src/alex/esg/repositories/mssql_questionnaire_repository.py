from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.repositories.questionnaire_repository import QuestionnaireRepository
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

class MssqlQuestionnaireRepository(
    QuestionnaireRepository
):
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

    def add(
        self,
        questionnaire: Questionnaire,
    ) -> Questionnaire:
        raise NotImplementedError(
            "MSSQL questionnaire creation "
            "is not implemented yet"
        )

    def list_all(
        self,
    ) -> tuple[Questionnaire, ...]:
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    questionnaire_code,
                    spec_version,
                    locale
                FROM dbo.QUESTIONNAIRE
                ORDER BY
                    questionnaire_code,
                    spec_version,
                    locale
                """
            )
            rows = cursor.fetchall()
            return tuple(self._map_row(row) for row in rows)
        finally:
            connection.close()

    def get_by_identity(
        self,
        *,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ) -> Questionnaire | None:
        connection = (self._connection_factory.connect())
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    questionnaire_code,
                    spec_version,
                    locale
                FROM dbo.QUESTIONNAIRE
                WHERE
                    questionnaire_code = ?
                    AND spec_version = ?
                    AND LOWER(locale) =
                        LOWER(?)
                """,
                questionnaire_code,
                spec_version,
                locale,
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._map_row(row)
        finally:
            connection.close()

    @staticmethod
    def _map_row(
        row,
    ) -> Questionnaire:
        return Questionnaire(
            questionnaire_code=row[0],
            spec_version=row[1],
            locale=row[2],
        )