import json

from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.question_definition_service import QuestionDefinitionService
from alex.esg.services.questionnaire_definition_file_import_service import QuestionnaireDefinitionFileImportService
from alex.esg.services.questionnaire_service import QuestionnaireService


def _create_service():
    questionnaire_service = (QuestionnaireService())

    definition_service = (QuestionDefinitionService())

    service = (
        QuestionnaireDefinitionFileImportService(
            json_service=JsonImportService(),
            definition_mapper=(
                QuestionnaireDefinitionMapper()
            ),
            questionnaire_service=(
                questionnaire_service
            ),
            question_definition_service=(
                definition_service
            ),
        )
    )

    return (
        service,
        questionnaire_service,
        definition_service,
    )


def _write_definition_file(
    tmp_path,
):
    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "ID_1",
                        "name": "E1",
                        "title": "Első kérdés",
                        "type": "text",
                        "category": "E",
                        "topic": "Teszt",
                        "organization": "SZTFH",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                    },
                    {
                        "ID": "ID_2",
                        "name": "E2",
                        "title": "Második kérdés",
                        "type": "text",
                        "category": "E",
                        "topic": "Teszt",
                        "organization": "SZTFH",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                    },
                ]
            }
        ],
    }

    file_path = (
        tmp_path
        / "definition.json"
    )

    file_path.write_text(json.dumps(data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return file_path

def test_definition_file_import_registers_questionnaire_and_definitions(tmp_path):
    (
        service,
        questionnaire_service,
        definition_service,
    ) = _create_service()

    definition_file = (_write_definition_file(tmp_path))

    result = service.import_file(
        definition_file=definition_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert result.questionnaire.questionnaire_code == ("SZTFH-ESG")
    assert (result.questionnaire.spec_version == "2.1")
    assert result.definition_count == 2
    assert result.added_count == 2
    assert result.reused_count == 0
    assert len(questionnaire_service.list_questionnaires()) == 1
    assert len(definition_service.list_definitions()) == 2
    assert all(definition.questionnaire is result.questionnaire for definition in result.definitions)

def test_definition_file_import_reuses_existing_definitions(tmp_path):
    (
        service,
        questionnaire_service,
        definition_service,
    ) = _create_service()

    definition_file = (_write_definition_file(tmp_path))

    first = service.import_file(
        definition_file=definition_file,
        questionnaire_code="SZTFH-ESG",
    )

    second = service.import_file(
        definition_file=definition_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert first.definition_count == 2
    assert second.definition_count == 2
    assert second.added_count == 0
    assert second.reused_count == 2
    assert (second.questionnaire is first.questionnaire)
    assert len(questionnaire_service.list_questionnaires()) == 1
    assert len(definition_service.list_definitions()) == 2
    assert (second.definitions[0] is first.definitions[0])
    assert (second.definitions[1] is first.definitions[1])