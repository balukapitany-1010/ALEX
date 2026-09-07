from alex.esg.repositories.mssql_question_definition_repository import MssqlQuestionDefinitionRepository
from alex.esg.repositories.mssql_submission_answer_loader import MssqlSubmissionAnswerLoader
from alex.esg.repositories.mssql_submission_repository import MssqlSubmissionRepository
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory


def main() -> None:
    config = (SqlServerConfig.from_environment())
    connection_factory = (SqlServerConnectionFactory(config))
    submission_repository = (MssqlSubmissionRepository(connection_factory))
    definition_repository = (MssqlQuestionDefinitionRepository(connection_factory))
    answer_loader = (MssqlSubmissionAnswerLoader(connection_factory=(connection_factory
            ),
            question_definition_repository=(definition_repository),
        )
    )

    submission = (submission_repository.get_by_id("1216"))

    if submission is None:
        print(
            "A 1216 submission "
            "nem található."
        )
        return

    print()
    print("Beküldés:")
    print(
        submission.submission_id,
        "|",
        submission.relation.requester.name,
        "|",
        submission.relation.supplier.name,
        "|",
        submission.questionnaire.spec_version,
    )

    print()
    print("Válaszok betöltése...")
    answer_loader.load(submission)
    print()
    print(f"Answer objektumok száma: " f"{len(submission.answers)}")
    print(f"Kitöltött válaszok száma: " f"{submission.answered_count}")
    print()
    print( "Első 20 Answer:")
    print("-" * 100)

    for answer in (submission.answers[:20]):
        definition = (answer.question_definition)

        print(
            definition.question.question_code,
            "|",
            definition.question.question_id,
            "|",
            definition.question_type.value,
            "|",
            len(answer.values),
            "value",
            "| answered:",
            answer.is_answered,
        )

        for value in answer.values:
            print(
                "   ",
                value.field_type,
                "| option:",
                value.option_id,
                "| selected:",
                value.selected,
                "| number:",
                value.number_value,
                "| text:",
                value.text_value,
            )


if __name__ == "__main__":
    main()