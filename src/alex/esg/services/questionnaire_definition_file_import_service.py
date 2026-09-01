from dataclasses import dataclass
from pathlib import Path

from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.question_definition_service import QuestionDefinitionService
from alex.esg.services.questionnaire_service import QuestionnaireService


@dataclass(frozen=True)
class QuestionnaireDefinitionFileImportResult:
    questionnaire: Questionnaire

    definitions: tuple[
        QuestionDefinition,
        ...
    ]

    added_definitions: tuple[
        QuestionDefinition,
        ...
    ]

    reused_definitions: tuple[
        QuestionDefinition,
        ...
    ]

    @property
    def definition_count(self) -> int:
        return len(self.definitions)

    @property
    def added_count(self) -> int:
        return len(self.added_definitions)

    @property
    def reused_count(self) -> int:
        return len(self.reused_definitions)


class QuestionnaireDefinitionFileImportService:
    def __init__(
        self,
        *,
        json_service: JsonImportService,
        definition_mapper: QuestionnaireDefinitionMapper,
        questionnaire_service: QuestionnaireService,
        question_definition_service: QuestionDefinitionService,
    ) -> None:
        if not isinstance(
            json_service,
            JsonImportService,
        ):
            raise TypeError("json_service must be a JsonImportService")

        if not isinstance(
            definition_mapper,
            QuestionnaireDefinitionMapper,
        ):
            raise TypeError(
                "definition_mapper must be a "
                "QuestionnaireDefinitionMapper"
            )

        if not isinstance(
            questionnaire_service,
            QuestionnaireService,
        ):
            raise TypeError(
                "questionnaire_service must be a "
                "QuestionnaireService"
            )

        if not isinstance(
            question_definition_service,
            QuestionDefinitionService,
        ):
            raise TypeError(
                "question_definition_service must be a "
                "QuestionDefinitionService"
            )

        self._json_service = json_service
        self._definition_mapper = ( definition_mapper)
        self._questionnaire_service = (questionnaire_service)
        self._question_definition_service = (question_definition_service)

    def import_file(
        self,
        *,
        definition_file: str | Path,
        questionnaire_code: str,
    ) -> QuestionnaireDefinitionFileImportResult:
        if not isinstance(
            questionnaire_code,
            str,
        ):
            raise TypeError("questionnaire_code must be a string")

        questionnaire_code = (questionnaire_code.strip())

        if not questionnaire_code:
            raise ValueError("questionnaire_code cannot be empty")

        definition_data = (self._json_service.load_file(definition_file))

        spec_version = definition_data.get("spec_version")

        locale = definition_data.get("locale")

        if not isinstance(
            spec_version,
            str,
        ):
            raise ValueError("definition spec_version must be a string")

        spec_version = (spec_version.strip())

        if not spec_version:
            raise ValueError("definition spec_version cannot be empty")

        if not isinstance(
            locale,
            str,
        ):
            raise ValueError("definition locale must be a string")

        locale = locale.strip()

        if not locale:
            raise ValueError("definition locale cannot be empty")

        questionnaire = (
            self._questionnaire_service.get_or_create(
                questionnaire_code=questionnaire_code,
                spec_version=spec_version,
                locale=locale,
            )
        )

        (
            mapped_questionnaire,
            mapped_definitions,
        ) = self._definition_mapper.map(
            definition_data,
            questionnaire_code=questionnaire_code,
            questionnaire=questionnaire,
        )

        registration = (self._question_definition_service.register_definitions(mapped_definitions))

        return QuestionnaireDefinitionFileImportResult(
            questionnaire=mapped_questionnaire,
            definitions=registration.definitions,
            added_definitions=registration.added,
            reused_definitions=registration.reused,
        )