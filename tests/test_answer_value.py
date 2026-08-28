import pytest

from alex.esg.domain.answer_value import (
    AnswerValue,
)


def test_answer_value_can_hold_selected_value():
    value = AnswerValue(
        field_type="single",
        option_id="04F1C68B_1",
        selected=True,
    )

    assert value.field_type == "single"
    assert value.option_id == "04F1C68B_1"
    assert value.selected is True
    assert value.is_answered is True


def test_answer_value_can_hold_unselected_value():
    value = AnswerValue(
        field_type="multi",
        option_id="3737695_1",
        selected=False,
    )

    assert value.selected is False
    assert value.is_answered is False


def test_answer_value_can_hold_text():
    value = AnswerValue(
        field_type="text",
        text_value="Teszt válasz",
    )

    assert value.text_value == "Teszt válasz"
    assert value.is_answered is True


def test_empty_text_is_not_answered():
    value = AnswerValue(
        field_type="text",
        text_value="",
    )

    assert value.is_answered is False


def test_answer_value_can_hold_number():
    value = AnswerValue(
        field_type="number",
        option_id="0319A12E_1",
        number_value=35.5,
    )

    assert value.number_value == 35.5
    assert value.is_answered is True


def test_zero_number_is_answered():
    value = AnswerValue(
        field_type="number",
        number_value=0,
    )

    assert value.is_answered is True


def test_number_value_rejects_bool():
    with pytest.raises(
        TypeError,
        match="number_value",
    ):
        AnswerValue(
            field_type="number",
            number_value=True,
        )


def test_answer_value_rejects_unknown_field_type():
    with pytest.raises(
        ValueError,
        match="unsupported field_type",
    ):
        AnswerValue(
            field_type="invalid",
        )


def test_text_field_rejects_number_value():
    with pytest.raises(
        ValueError,
        match="text field cannot have number_value",
    ):
        AnswerValue(
            field_type="text",
            number_value=10,
        )


def test_number_field_rejects_text_value():
    with pytest.raises(
        ValueError,
        match="number field cannot have text_value",
    ):
        AnswerValue(
            field_type="number",
            text_value="10",
        )


def test_selection_field_rejects_number_value():
    with pytest.raises(
        ValueError,
        match="cannot have number_value",
    ):
        AnswerValue(
            field_type="multi",
            option_id="TEST_1",
            number_value=10,
        )


def test_option_id_is_optional():
    value = AnswerValue(
        field_type="number",
        number_value=42,
    )

    assert value.option_id is None
