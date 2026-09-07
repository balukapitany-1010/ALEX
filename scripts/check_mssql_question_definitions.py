from collections import Counter
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.repositories.mssql_question_definition_repository import MssqlQuestionDefinitionRepository
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def main() -> None:
    config = (SqlServerConfig.from_environment())
    connection_factory = (SqlServerConnectionFactory(config))
    repository = (MssqlQuestionDefinitionRepository(connection_factory))
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.0",
        locale="HU",
    )
    definitions = (repository.list_for_questionnaire(questionnaire))
    print()
    print("Kérdésdefiníciók ellenőrzése")
    print(f"Definíciók száma: " f"{len(definitions)}")

    counts = Counter(definition.question_type.value for definition in definitions)

    print()
    print("Típusok:")

    for (
        question_type,
        count,
    ) in sorted(
        counts.items()
    ):
        print(f"  {question_type}: {count}")

    print()
    print("Első 20 kérdés:")

    for definition in definitions[:20]:
        print(
            definition.question.question_id,
            "|",
            definition.question.question_code,
            "|",
            definition.question_type.value,
            "|",
            len(definition.options),
            "opció",
            "|",
            definition.title,
        )


if __name__ == "__main__":
    main()