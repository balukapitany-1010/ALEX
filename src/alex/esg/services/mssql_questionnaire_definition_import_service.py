from pathlib import Path
from alex.esg.repositories.mssql_questionnaire_definition_writer import MssqlQuestionnaireDefinitionWriter
from alex.esg.services.json_import_service import JsonImportService

class MssqlQuestionnaireDefinitionImportService:
    def __init__(
        self,
        *,
        json_import_service: JsonImportService,
        writer: MssqlQuestionnaireDefinitionWriter,
    ) -> None:
        if not isinstance(
            json_import_service,
            JsonImportService,
        ):
            raise TypeError(
                "json_import_service must be a "
                "JsonImportService"
            )

        if not isinstance(
            writer,
            MssqlQuestionnaireDefinitionWriter,
        ):
            raise TypeError(
                "writer must be a "
                "MssqlQuestionnaireDefinitionWriter"
            )
        self._json_import_service = (json_import_service)
        self._writer = writer

    def import_file(
        self,
        file_path: str | Path,
        *,
        questionnaire_code: str = "SZTFH",
    ) -> None:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError( f"definition file not found: {path}")
        if not path.is_file():
            raise ValueError(f"definition path is not a file: {path}")
        if path.suffix.lower() != ".json":
            raise ValueError("definition file must be a JSON file")

        data = (self._json_import_service.load_file(path))
        self._writer.write(
            data=data,
            questionnaire_code=(questionnaire_code),
        )