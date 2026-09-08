from alex.esg.services.submission_persistence_validator import SubmissionPersistenceValidator
from decimal import Decimal

def create_payload(
    number_value,
):
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
                    "id": "TEST_Q",
                    "question_id": "TEST",
                    "fields": [
                        {
                            "type": "number",
                            "values": [
                                {
                                    "optionId": (
                                        "TEST_Q_1"
                                    ),
                                    "value": (
                                        number_value
                                    ),
                                }
                            ],
                        }
                    ],
                }
            ],
        },
    }


def test_validator_returns_valid_result():
    result = (SubmissionPersistenceValidator.validate(
            submission_index=1,
            submission_payload=(create_payload(12.5)),
            batch_id="BATCH_TEST",
            relation_id=274,
            supplier_tax_number=("11102481207"),
            questionnaire_question_ids={"TEST_Q",},
            option_ids_by_question={"TEST_Q": {"TEST_Q_1",}},
        )
    )

    assert result.is_valid is True
    assert result.error is None
    assert result.answer_count == 1
    assert result.answer_value_count == 1


def test_validator_accepts_scientific_number():
    result = (SubmissionPersistenceValidator.validate(
            submission_index=1,
            submission_payload=(create_payload( "6E-06")),
            batch_id="BATCH_TEST",
            relation_id=274,
            supplier_tax_number=("11102481207"),
            questionnaire_question_ids={"TEST_Q",},
            option_ids_by_question={"TEST_Q": {"TEST_Q_1",}},
        )
    )

    assert result.is_valid is True
    assert result.error is None
    assert result.plan is not None
    assert (result.plan.answers[0].values[0].number_value == Decimal("0.0000"))