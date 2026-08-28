import pytest

from alex.esg.mappers.submission_header_mapper import (
    SubmissionHeaderMapper,
)


def test_submission_header_mapper_maps_header():
    data = {
        "response": {
            "respondent_id": "RESP-1",
            "respondent_MP_id": "MP-123",
            "org_size": "Large",
            "submitted_at": "2026-02-12T11:54:29Z",
            "cover": {
                "supplier": {
                    "company": "Minta Beszállító Kft.",
                    "tax_number": "12345678-2-41",
                    "period": "2026-Q1",
                },
                "requester": {
                    "company": "ABC Zrt.",
                    "tax_number": "87654321-2-41",
                    "requester_MP_id": "REQ-123",
                },
            },
        }
    }

    mapper = SubmissionHeaderMapper()

    result = mapper.map(data)

    assert (
        result.supplier_company
        == "Minta Beszállító Kft."
    )

    assert (
        result.supplier_tax_number
        == "12345678-2-41"
    )

    assert result.requester_company == "ABC Zrt."
    assert result.requester_tax_number == "87654321-2-41"
    assert result.requester_mp_id == "REQ-123"

    assert result.respondent_id == "RESP-1"
    assert result.respondent_mp_id == "MP-123"

    assert result.org_size == "Large"

    assert (
        result.submitted_at
        == "2026-02-12T11:54:29Z"
    )

    assert result.period == "2026-Q1"


def test_submission_header_mapper_converts_empty_strings_to_none():
    data = {
        "response": {
            "respondent_id": None,
            "respondent_MP_id": None,
            "org_size": None,
            "submitted_at": "2026-02-12T11:54:29Z",
            "cover": {
                "supplier": {
                    "company": "Minta Beszállító Kft.",
                    "tax_number": "",
                    "period": "",
                },
                "requester": {
                    "company": "",
                    "tax_number": "",
                    "requester_MP_id": None,
                },
            },
        }
    }

    mapper = SubmissionHeaderMapper()

    result = mapper.map(data)

    assert (
        result.supplier_company
        == "Minta Beszállító Kft."
    )

    assert result.supplier_tax_number is None

    assert result.requester_company is None
    assert result.requester_tax_number is None
    assert result.requester_mp_id is None

    assert result.period is None


def test_submission_header_mapper_rejects_missing_response():
    mapper = SubmissionHeaderMapper()

    with pytest.raises(
        ValueError,
        match="submission response must be an object",
    ):
        mapper.map({})


def test_submission_header_mapper_rejects_missing_cover():
    mapper = SubmissionHeaderMapper()

    with pytest.raises(
        ValueError,
        match="response cover must be an object",
    ):
        mapper.map(
            {
                "response": {}
            }
        )