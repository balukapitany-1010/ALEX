import sys
from pathlib import Path
from alex.esg.repositories.mssql_questionnaire_definition_writer import MssqlQuestionnaireDefinitionWriter
from alex.esg.services.json_import_service import JsonImportService
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

QUESTIONNAIRE_CODE = "SZTFH"
def main() -> None:
    if len(sys.argv) != 3:
        print("Használat:" )
        print(
            "python "
            "scripts\\write_mssql_"
            "questionnaire_definition.py "
            "\"<definition.json>\" "
            "--execute"
        )
        raise SystemExit(2)
    definition_file = Path(sys.argv[1])
    execute_flag = (sys.argv[2].strip().lower())
    if execute_flag != "--execute":
        print("Írás megszakítva.")
        print(
            "A tényleges adatbázis-íráshoz "
            "meg kell adni a --execute kapcsolót."
        )
        raise SystemExit(2)
    json_service = (JsonImportService())
    data = (json_service.load_file(definition_file))
    spec_version = data.get("spec_version")
    locale = data.get("locale")
    print()
    print("MSSQL kérdőív-definíció írás")
    print("=" * 60)
    print("Fájl:", definition_file,)
    print(
        "Kérdőív:",
        QUESTIONNAIRE_CODE,
        spec_version,
        locale,
    )
    print()
    print("FIGYELEM: ez a futás már "
        "ír az adatbázisba."
    )
    print()
    config = (SqlServerConfig.from_environment())
    connection_factory = (SqlServerConnectionFactory(config))
    writer = (MssqlQuestionnaireDefinitionWriter(connection_factory))
    writer.write(
        data=data,
        questionnaire_code=(QUESTIONNAIRE_CODE),
    )
    print()
    print("Írás sikeresen befejeződött.")
    print("A tranzakció COMMIT megtörtént.")

if __name__ == "__main__":
    main()