import pytest

from alex.esg.mappers.submission_answer_mapper import (
    SubmissionAnswerMapper,
)


def test_mapper_maps_single_field():
    data = {
        "id": "04F1C68B",
        "question_id": "E2",
        "fields": [
            {
                "type": "single",
                "values": [
                    {
                        "optionId": "04F1C68B_1",
                        "selected": True,
                    },
                    {
                        "optionId": "04F1C68B_2",
                        "selected": False,
                    },
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 2

    assert values[0].field_type == "single"
    assert values[0].option_id == "04F1C68B_1"
    assert values[0].selected is True

    assert values[1].selected is False


def test_mapper_maps_text_field():
    data = {
        "id": "04F1C68B_DETAIL",
        "question_id": "E2_detail",
        "fields": [
            {
                "type": "text",
                "values": [
                    {
                        "value": "Teszt szöveg"
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1
    assert values[0].field_type == "text"
    assert values[0].text_value == "Teszt szöveg"
    assert values[0].is_answered is True


def test_mapper_maps_number_field():
    data = {
        "id": "0364FD79",
        "question_id": "E5",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0364FD79_1",
                        "value": 1250.5,
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1

    assert (
        values[0].option_id
        == "0364FD79_1"
    )

    assert values[0].number_value == 1250.5


def test_mapper_maps_mixed_question_fields():
    data = {
        "id": "0319A12E",
        "question_id": "E6",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_1",
                        "value": 25.5,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_2",
                        "value": 10.0,
                    }
                ],
            },
            {
                "type": "number",
                "values": [
                    {
                        "optionId": "0319A12E_3",
                        "value": 24.1,
                    }
                ],
            },
            {
                "type": "multi",
                "values": [
                    {
                        "optionId": "0319A12E_4",
                        "selected": False,
                    }
                ],
            },
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 4

    assert values[0].number_value == 25.5
    assert values[1].number_value == 10.0
    assert values[2].number_value == 24.1

    assert values[3].field_type == "multi"
    assert values[3].selected is False

def test_mapper_allows_number_without_option_id():
    data = {
        "id": "TEST",
        "question_id": "TEST",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "value": None
                    }
                ],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    values = mapper.map_values(data)

    assert len(values) == 1
    assert values[0].option_id is None
    assert values[0].number_value is None
    assert values[0].is_answered is False

def test_mapper_rejects_unknown_field_type():
    data = {
        "id": "TEST",
        "question_id": "TEST",
        "fields": [
            {
                "type": "invalid",
                "values": [],
            }
        ],
    }

    mapper = SubmissionAnswerMapper()

    with pytest.raises(
        ValueError,
        match="unsupported field type",
    ):
        mapper.map_values(data)