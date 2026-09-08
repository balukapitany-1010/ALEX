from decimal import Decimal
import pytest
from alex.esg.services.answer_value_persistence_mapper import AnswerValuePersistenceMapper


def test_maps_single_value():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="single",
            raw_value={
                "optionId": "A_1",
                "selected": True,
            },
            questionnaire_option_ids={
                "A_1",
                "A_2",
            },
        )
    )

    assert result.field_type == "single"
    assert result.option_id == "A_1"
    assert result.selected is True
    assert result.number_value is None
    assert result.text_value is None


def test_maps_multi_false_value():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="multi",
            raw_value={
                "optionId": "A_2",
                "selected": False,
            },
            questionnaire_option_ids={
                "A_1",
                "A_2",
            },
        )
    )

    assert result.option_id == "A_2"
    assert result.selected is False


def test_removes_option_not_in_questionnaire_version():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="number",
            raw_value={
                "optionId": "04E40FB9_16",
                "value": None,
            },
            questionnaire_option_ids=set(),
        )
    )
    assert result.option_id is None
    assert result.number_value is None

def test_maps_number_value():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="number",
            raw_value={
                "optionId": "0364FD79_1",
                "value": 53.95,
            },
            questionnaire_option_ids={
                "0364FD79_1",
            },
        )
    )

    assert (result.option_id == "0364FD79_1")
    assert (result.number_value == Decimal("53.9500"))

def test_maps_null_number():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="number",
            raw_value={
                "optionId": "03182D16_1",
                "value": None,
            },
            questionnaire_option_ids={
                "03182D16_1",
            },
        )
    )

    assert result.number_value is None

def test_rounds_scientific_number_to_decimal_scale():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="number",
            raw_value={
                "optionId": "043A300C_1",
                "value": "6E-06",
            },
            questionnaire_option_ids={"043A300C_1",},
        )
    )
    assert (result.option_id == "043A300C_1")
    assert (result.number_value == Decimal("0.0000"))

def test_maps_text_value():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="text",
            raw_value={
                "value": "Energetikai audit",
            },
            questionnaire_option_ids=set(),
        )
    )

    assert (result.text_value == "Energetikai audit")
    assert result.option_id is None


def test_maps_null_text_value():
    result = (AnswerValuePersistenceMapper.map_value(
            field_type="text",
            raw_value={
                "value": None,
            },
            questionnaire_option_ids=set(),
        )
    )

    assert result.text_value is None


def test_maps_all_fields_of_mixed_question():
    fields = [
        {
            "type": "number",
            "values": [
                {
                    "optionId": "Q_1",
                    "value": 12.5,
                }
            ],
        },
        {
            "type": "multi",
            "values": [
                {
                    "optionId": "Q_2",
                    "selected": False,
                }
            ],
        },
    ]

    result = (AnswerValuePersistenceMapper.map_fields(
            fields=fields,
            questionnaire_option_ids={
                "Q_1",
                "Q_2",
            },
        )
    )

    assert len(result) == 2
    assert (result[0].number_value == Decimal("12.5000"))
    assert result[1].selected is False

def test_rejects_invalid_single_option():
    with pytest.raises(
        ValueError,
        match="option_id is not valid",
    ):
        (
            AnswerValuePersistenceMapper.map_value(
                field_type="single",
                raw_value={
                    "optionId": "WRONG_1",
                    "selected": True,
                },
                questionnaire_option_ids={
                    "Q_1",
                    "Q_2",
                },
            )
        )