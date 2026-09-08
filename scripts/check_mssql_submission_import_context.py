from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import MssqlSubmissionImportContextReader
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def main() -> None:
    config = (SqlServerConfig.from_environment())
    factory = (SqlServerConnectionFactory(config))
    reader = (MssqlSubmissionImportContextReader(factory))
    context = reader.load_context(
        batch_id=("BATCH_11107792244_20260507135421"),
        questionnaire_code="SZTFH",
        spec_version="2.0",
    )

    relation_id = (reader.resolve_relation_id(
            requester_tax_number=("11107792-2-44"),
            supplier_tax_number=("11102481207"),
        )
    )

    print()
    print("SUBMISSION IMPORT CONTEXT CHECK")
    print("=" * 70)
    print("batch_id:", context.batch_id,)
    print("questionnaire:", context.questionnaire_code,)
    print("spec_version:",context.spec_version,)
    print("questionnaire question:", len(context.questionnaire_question_ids),)
    print("relation_id:", relation_id,)
    print()
    print("ADATBÁZIS-ÍRÁS: 0 rekord")
if __name__ == "__main__":
    main()