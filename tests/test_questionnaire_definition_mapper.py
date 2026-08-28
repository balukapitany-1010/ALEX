import json
from pathlib import Path
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_type import QuestionType
from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)


def test_mapper_maps_questionnaire_definition():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "3737695",
                        "name": "E1",
                        "title": "Teszt kérdés",
                        "type": "checkbox",
                        "category": "E",
                        "topic": "Zöld minősítés",
                        "subtopic": "",
                        "requirement": "Teszt követelmény",
                        "organization_size": [
                            "Large",
                            "Medium",
                        ],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland",
                        ],
                        "organization": "SZTFH",
                        "choices": [
                            {
                                "text": "Igen",
                                "value": "3737695_1",
                            },
                            {
                                "text": "Nem",
                                "value": "3737695_2",
                            },
                        ],
                    }
                ]
            }
        ],
    }

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert questionnaire.questionnaire_code == "SZTFH-ESG"
    assert questionnaire.spec_version == "2.0"
    assert questionnaire.locale == "HU"

    assert len(definitions) == 1

    definition = definitions[0]

    assert definition.question.question_id == "3737695"
    assert definition.question.question_code == "E1"

    assert definition.category is QuestionCategory.E
    assert definition.question_type is QuestionType.CHECKBOX

    assert definition.title == "Teszt kérdés"
    assert definition.topic == "Zöld minősítés"

    assert len(definition.options) == 2

    assert definition.options[0].option_id == "3737695_1"
    assert definition.options[0].label == "Igen"

def test_mapper_maps_comment_question_type():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "TEST_COMMENT",
                        "name": "E_TEST_DETAIL",
                        "title": "Részletezze a választ.",
                        "type": "comment",
                        "category": "E",
                        "topic": "Teszt",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                        "organization": "SZTFH",
                    }
                ]
            }
        ],
    }

    mapper = QuestionnaireDefinitionMapper()

    _, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert (
        definitions[0].question_type
        is QuestionType.COMMENT
    )


def test_mapper_maps_table_question_type():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "TEST_TABLE",
                        "name": "E_TEST_TABLE",
                        "title": "Teszt táblázat",
                        "type": "table",
                        "category": "E",
                        "topic": "Teszt",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                        "organization": "SZTFH",
                        "rows": 5,
                        "columns": [],
                    }
                ]
            }
        ],
    }

    mapper = QuestionnaireDefinitionMapper()

    _, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert (
        definitions[0].question_type
        is QuestionType.TABLE
    )

def test_mapper_maps_real_questionnaire_definition():
    file_path = (
        Path(__file__).parent
        / "data"
        / "Sztfh_kerdoiv_2_0_HU.json"
    )

    with file_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    mapper = QuestionnaireDefinitionMapper()

    questionnaire, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert questionnaire.spec_version == "2.0"
    assert questionnaire.locale == "HU"

    assert len(definitions) > 0

    first_definition = definitions[0]

    assert first_definition.question.question_id == "3737695"
    assert first_definition.question.question_code == "E1"
    assert first_definition.category is QuestionCategory.E
    assert first_definition.question_type is QuestionType.CHECKBOX

def test_mapper_accepts_mixed_detail_without_title():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "01E0389E_DETAIL",
                        "name": "E30_detail",
                        "type": "mixed",
                        "category": "E",
                        "topic": "Víz",
                        "subtopic": "Vízfelhasználás",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                        "organization": "SZTFH",
                        "choices": [
                            {
                                "text": "a következő dátummal:",
                                "value": "01E0389E_detail1",
                            }
                        ],
                    }
                ]
            }
        ],
    }

    mapper = QuestionnaireDefinitionMapper()

    _, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert definitions[0].title == "E30_detail"
    assert (
        definitions[0].question_type
        is QuestionType.MIXED
    )

def test_mapper_ignores_inactive_option_with_empty_label():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "TEST_CHECKBOX",
                        "name": "TEST",
                        "title": "Teszt kérdés",
                        "type": "checkbox",
                        "category": "E",
                        "topic": "Teszt",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                        "organization": "SZTFH",
                        "choices": [
                            {
                                "text": "Aktív opció",
                                "value": "TEST_1",
                                "status": "active",
                            },
                            {
                                "text": "",
                                "value": "TEST_2",
                                "status": "inactive",
                            },
                        ],
                    }
                ]
            }
        ],
    }

    mapper = QuestionnaireDefinitionMapper()

    _, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    assert len(definitions[0].options) == 1
    assert (
        definitions[0].options[0].option_id
        == "TEST_1"
    )