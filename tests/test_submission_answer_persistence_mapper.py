from decimal import Decimal
import pytest
from alex.esg.services.submission_answer_persistence_mapper import SubmissionAnswerPersistenceMapper


def test_maps_valid_question():
    payload = {
        "id": "0364FD79",
        "question_id": "E5",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": (
                            "0364FD79_1"
                        ),
                        "value": 53.95,
                    }
                ],
            }
        ],
    }

    result = (SubmissionAnswerPersistenceMapper.map_question(
            question_payload=payload,
            questionnaire_question_ids={"0364FD79",},
            option_ids_by_question={"0364FD79": {"0364FD79_1",}},
        )
    )

    assert result is not None
    assert (result.question_id == "0364FD79")

    assert len(result.values) == 1
    assert (result.values[0].number_value == Decimal("53.9500"))

def test_skips_question_not_in_version():
    payload = {
        "id": "034FEA08_DETAIL",
        "question_id": "S2_detail",
        "fields": [
            {
                "type": "text",
                "values": [
                    {
                        "value": None,
                    }
                ],
            }
        ],
    }

    result = (SubmissionAnswerPersistenceMapper.map_question(
            question_payload=payload,
            questionnaire_question_ids={"034FEA08",},
            option_ids_by_question={},
        )
    )

    assert result is None


def test_number_option_can_be_removed():
    payload = {
        "id": "043564F5_DETAIL",
        "question_id": "E43_detail",
        "fields": [
            {
                "type": "number",
                "values": [
                    {
                        "optionId": (
                            "043564F5_DETAIL"
                        ),
                        "value": None,
                    }
                ],
            }
        ],
    }

    result = (SubmissionAnswerPersistenceMapper.map_question(
            question_payload=payload,
            questionnaire_question_ids={"043564F5_DETAIL",},
            option_ids_by_question={"043564F5_DETAIL": set(),},
        )
    )

    assert result is not None
    assert len(result.values) == 1
    assert result.values[0].option_id is None
    assert result.values[0].number_value is None


def test_rejects_single_option_from_wrong_question():
    payload = {
        "id": "TEST_Q",
        "question_id": "TEST",
        "fields": [
            {
                "type": "single",
                "values": [
                    {
                        "optionId": "OTHER_1",
                        "selected": True,
                    }
                ],
            }
        ],
    }

    with pytest.raises(
        ValueError,
        match="option_id is not valid",
    ):
        (
            SubmissionAnswerPersistenceMapper.map_question(
                question_payload=payload,
                questionnaire_question_ids={"TEST_Q",},
                option_ids_by_question={"TEST_Q": {"TEST_Q_1",}},
            )
        )