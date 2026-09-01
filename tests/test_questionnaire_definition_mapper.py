import json
import pytest
from pathlib import Path
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_type import QuestionType
from alex.esg.mappers.questionnaire_definition_mapper import (
    QuestionnaireDefinitionMapper,
)
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.json_import_service import JsonImportService


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

def test_mapper_detail_inherits_previous_topic():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "048E497F",
                        "name": "G1b",
                        "title": "Főkérdés",
                        "type": "checkbox",
                        "category": "G",
                        "topic": "Vállalkozási irányítási rendszerek",
                        "organization": "SZTFH",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                        "choices": [
                            {
                                "value": "048E497F_1",
                                "text": "Teszt",
                                "status": "active",
                            }
                        ],
                    },
                    {
                        "ID": "048E497F_DETAIL1",
                        "name": "G1b_detail1",
                        "title": "Részletezés",
                        "type": "text",
                        "category": "G",
                        "organization": "SZTFH",
                        "organization_size": ["Large"],
                        "GeographicalRelevance": [
                            "HU/EGT/Switzerland"
                        ],
                    },
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
        definitions[1].topic
        == "Vállalkozási irányítási rendszerek"
    )

def test_mapper_maps_table_allowed_value_ids():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E17a",
                        "title": (
                            "Célkitűzések táblázata"
                        ),
                        "type": "table",
                        "category": "E",
                        "ID": "04E40FB9",
                        "topic": "Éghajlatváltozás",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                        "organization": "SZTFH",
                        "columns": [
                            {
                                "key": "column1",
                                "cellType": "text",
                                "cells": [
                                    {
                                        "value": (
                                            "04E40FB9_1"
                                        )
                                    },
                                    {
                                        "value": (
                                            "04E40FB9_2"
                                        )
                                    },
                                ],
                            },
                            {
                                "key": "column2",
                                "cellType": "number",
                                "cells": [
                                    {
                                        "value": (
                                            "04E40FB9_3"
                                        )
                                    }
                                ],
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

    definition = definitions[0]

    assert (
        definition.allowed_value_ids
        == (
            "04E40FB9_1",
            "04E40FB9_2",
            "04E40FB9_3",
        )
    )

def test_mapper_maps_mixed_allowed_value_ids():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E6",
                        "title": "Teszt",
                        "type": "mixed",
                        "category": "E",
                        "ID": "0319A12E",
                        "topic": "Éghajlatváltozás",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                        "organization": "SZTFH",
                        "choices": [
                            {
                                "text": "Első",
                                "value": "0319A12E_1",
                                "inputType": "number",
                            },
                            {
                                "text": "Második",
                                "value": "0319A12E_2",
                                "inputType": "number",
                            },
                            {
                                "text": "Harmadik",
                                "value": "0319A12E_3",
                                "inputType": "number",
                            },
                            {
                                "text": "Nem ismert",
                                "value": "0319A12E_4",
                                "inputType": "checkbox",
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

    assert (
        definitions[0].allowed_value_ids
        == (
            "0319A12E_1",
            "0319A12E_2",
            "0319A12E_3",
            "0319A12E_4",
        )
    )
def test_mapper_maps_real_e17a_table_value_ids():
    file_path = (
        Path(__file__).parent
        / "data"
        / "Sztfh_kerdoiv_2_0_HU.json"
    )

    import_service = JsonImportService()

    data = import_service.load_file(
        file_path
    )

    mapper = QuestionnaireDefinitionMapper()

    _, definitions = mapper.map(
        data,
        questionnaire_code="SZTFH-ESG",
    )

    definition = next(
        definition
        for definition in definitions
        if (
            definition.question.question_code
            == "E17a"
        )
    )

    assert (
        definition.question.question_id
        == "04E40FB9"
    )

    assert (
        "04E40FB9_1"
        in definition.allowed_value_ids
    )

    assert (
        "04E40FB9_30"
        in definition.allowed_value_ids
    )

    assert (
        len(
            definition.allowed_value_ids
        )
        == 30
    )

def test_mapper_uses_question_id_for_standalone_number_value():
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E43_detail",
                        "title": "Céldátum",
                        "type": "number",
                        "category": "E",
                        "ID": "043564F5_DETAIL",
                        "topic": (
                            "Hulladék, "
                            "körforgásos gazdaság"
                        ),
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [],
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

    assert len(definitions) == 1

    assert (
        definitions[0].allowed_value_ids
        == (
            "043564F5_DETAIL",
        )
    )

def test_mapper_uses_existing_questionnaire():
    mapper = QuestionnaireDefinitionMapper()

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "ID": "TEST_ID",
                        "name": "E1",
                        "title": "Teszt kérdés",
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
                    }
                ]
            }
        ],
    }

    result_questionnaire, definitions = (
        mapper.map(
            data,
            questionnaire_code="SZTFH-ESG",
            questionnaire=questionnaire,
        )
    )

    assert (
        result_questionnaire
        is questionnaire
    )

    assert len(definitions) == 1

    assert (
        definitions[0].questionnaire
        is questionnaire
    )
def test_mapper_rejects_existing_questionnaire_with_wrong_version():
    mapper = QuestionnaireDefinitionMapper()

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.0",
        locale="HU",
    )

    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [
            {
                "elements": []
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match=(
            "questionnaire version does not match "
            "definition spec_version"
        ),
    ):
        mapper.map(
            data,
            questionnaire_code="SZTFH-ESG",
            questionnaire=questionnaire,
        )
def test_mapper_accepts_existing_questionnaire_locale_case_difference():
    mapper = QuestionnaireDefinitionMapper()

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [
            {
                "elements": []
            }
        ],
    }

    result_questionnaire, definitions = (
        mapper.map(
            data,
            questionnaire_code="SZTFH-ESG",
            questionnaire=questionnaire,
        )
    )

    assert (
        result_questionnaire
        is questionnaire
    )

    assert definitions == ()