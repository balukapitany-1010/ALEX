from decimal import Decimal
import pytest
from alex.esg.services.submission_persistence_plan import SubmissionPersistencePlanner

def create_payload():
    return {
        "supplier_key": None,
        "response": {
            "respondent_id": None,
            "respondent_MP_id": None,
            "org_size": None,
            "submitted_at": (
                "2026-02-26T07:39:59Z"
            ),
            "cover": {
                "supplier": {
                    "tax_number": (
                        "11102481207"
                    ),
                    "period": "2024",
                }
            },
            "questions": [
                {
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
                },
                {
                    "id": (
                        "034FEA08_DETAIL"
                    ),
                    "question_id": (
                        "S2_detail"
                    ),
                    "fields": [
                        {
                            "type": "text",
                            "values": [
                                {
                                    "value": None
                                }
                            ],
                        }
                    ],
                },
            ],
        },
    }


def test_creates_complete_plan():
    result = (SubmissionPersistencePlanner.create_plan(
            submission_payload=(create_payload()),
            batch_id="BATCH_TEST",
            relation_id=274,
            questionnaire_question_ids={"0364FD79",},
            option_ids_by_question={"0364FD79": {"0364FD79_1",}},
        )
    )

    assert (result.submission.batch_id == "BATCH_TEST")
    assert (result.submission.relation_id == 274)
    assert (result.submission.respondent_id == "RESP_11102481207_2024")
    assert result.answer_count == 1
    assert (result.answer_value_count == 1)
    assert (result.answers[0].question_id == "0364FD79")
    assert (result.answers[0].values[0].number_value == Decimal("53.9500"))
    assert (result.skipped_question_ids == ("034FEA08_DETAIL",))

def test_rejects_duplicate_question_id():
    payload = create_payload()

    payload[
        "response"
    ][
        "questions"
    ].append(
        {
            "id": "0364FD79",
            "question_id": "E5",
            "fields": [],
        }
    )

    with pytest.raises(
        ValueError,
        match="duplicate question id",
    ):
        (
            SubmissionPersistencePlanner.create_plan(
                submission_payload=payload,
                batch_id="BATCH_TEST",
                relation_id=274,
                questionnaire_question_ids={"0364FD79",},
                option_ids_by_question={"0364FD79": {"0364FD79_1",}},
            )
        )


def test_scientific_number_is_rounded_in_plan():
    payload = create_payload()
    payload[
        "response"
    ][
        "questions"
    ][0][
        "fields"
    ][0][
        "values"
    ][0][
        "value"
    ] = "6E-06"

    result = (SubmissionPersistencePlanner.create_plan(
            submission_payload=payload,
            batch_id="BATCH_TEST",
            relation_id=274,
            questionnaire_question_ids={"0364FD79",},
            option_ids_by_question={"0364FD79": {"0364FD79_1",}},
        )
    )
    assert result.answer_count == 1
    assert (result.answers[0].values[0].number_value == Decimal("0.0000"))