from unittest.mock import MagicMock
from alex.esg.repositories.mssql_questionnaire_definition_writer import MssqlQuestionnaireDefinitionWriter
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.mssql_questionnaire_definition_import_service import MssqlQuestionnaireDefinitionImportService

def test_import_service_loads_json_and_calls_writer(tmp_path,):
    definition_file = ( tmp_path / "definition.json")
    definition_file.write_text(
        "{}",
        encoding="utf-8",
    )
    json_import_service = MagicMock(spec=JsonImportService)
    writer = MagicMock(spec=MssqlQuestionnaireDefinitionWriter)
    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [],
    }
    json_import_service.load_file.return_value = (data)
    service = (MssqlQuestionnaireDefinitionImportService(
            json_import_service=(json_import_service),
            writer=writer,
        )
    )

    service.import_file(definition_file)
    json_import_service.load_file.assert_called_once_with(definition_file)
    writer.write.assert_called_once_with(
        data=data,
        questionnaire_code="SZTFH",
    )