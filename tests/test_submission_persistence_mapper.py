import json
from datetime import datetime
from alex.esg.services.submission_persistence_mapper import SubmissionPersistenceMapper

def create_payload() -> dict:
    return {
        "supplier_key": None,
        "response": {
            "survey_type": "SZTFH",
            "respondent_id": None,
            "respondent_MP_id": None,
            "org_size": None,
            "submitted_at": (
                "2026-02-26T07:39:59Z"
            ),
            "cover": {
                "supplier": {
                    "company": (
                        "Teszt Beszállító Kft."
                    ),
                    "tax_number": (
                        "11102481207"
                    ),
                    "period": "2024",
                },
                "requester": {
                    "company": (
                        "Yettel Magyarország Zrt."
                    ),
                    "requester_MP_id": None,
                    "tax_number": (
                        "11107792-2-44"
                    ),
                },
            },
            "questions": [],
        },
    }

def test_normalizes_requester_tax_number():
    assert (SubmissionPersistenceMapper.normalize_tax_number("11107792-2-44") == "11107792244")

def test_creates_external_supplier_key():
    assert (SubmissionPersistenceMapper.create_external_supplier_key("11102481207") == "SUP_11102481207")

def test_creates_respondent_id():
    assert (SubmissionPersistenceMapper.create_respondent_id(
            "11102481207",
            "2024",) == "RESP_11102481207_2024")


def test_creates_noperiod_respondent_id():
    assert (SubmissionPersistenceMapper.create_respondent_id(
            "11102481207",
            None,
        ) == "RESP_11102481207_NOPERIOD")


def test_creates_batch_id():
    created_at = datetime(
        2026,
        5,
        7,
        13,
        54,
        21,
    )

    assert (SubmissionPersistenceMapper.create_batch_id(
            "11107792-2-44",
            created_at,
        ) == "BATCH_11107792244_20260507135421")

def test_parses_utc_submitted_at():
    result = (SubmissionPersistenceMapper.parse_submitted_at("2026-02-26T07:39:59Z"))

    assert result == datetime(
        2026,
        2,
        26,
        7,
        39,
        59,
    )


def test_maps_yettel_submission_header():
    payload = {
        "supplier_key": None,
        "response": {
            "survey_type": "SZTFH",
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
        },
    }

    result = (SubmissionPersistenceMapper.map_submission(
            submission_payload=payload,
            batch_id=(
                "BATCH_11107792244_"
                "20260507135421"
            ),
            relation_id=274,
        )
    )

    assert result.batch_id == (
        "BATCH_11107792244_"
        "20260507135421"
    )

    assert result.relation_id == 274
    assert (result.external_supplier_key == "SUP_11102481207")
    assert (result.respondent_id == "RESP_11102481207_2024")
    assert result.respondent_mp_id is None
    assert result.org_size is None
    assert result.submitted_at == datetime(
        2026,
        2,
        26,
        7,
        39,
        59,
    )

    assert (result.status == "imported_complete")

def test_preserves_existing_identifiers():
    payload = {
        "supplier_key": (
            "SUP_ALREADY_PRESENT"
        ),
        "response": {
            "respondent_id": (
                "RESP_ALREADY_PRESENT"
            ),
            "submitted_at": None,
            "cover": {
                "supplier": {
                    "tax_number": (
                        "11102481207"
                    ),
                    "period": "2024",
                }
            },
        },
    }

    result = (SubmissionPersistenceMapper.map_submission(
            submission_payload=payload,
            batch_id="BATCH_TEST",
            relation_id=123,
        )
    )
    assert (result.external_supplier_key == "SUP_ALREADY_PRESENT")
    assert (result.respondent_id == "RESP_ALREADY_PRESENT")

def test_raw_payload_contains_top_level_requester():
    payload = create_payload()

    payload[
        "response"
    ][
        "cover"
    ][
        "requester"
    ] = {
        "company": (
            "Yettel Magyarország Zrt."
        ),
        "requester_MP_id": None,
        "tax_number": (
            "11107792-2-44"
        ),
    }

    result = (
        SubmissionPersistenceMapper
        .map_submission(
            submission_payload=payload,
            batch_id="BATCH_TEST",
            relation_id=274,
        )
    )

    raw_payload = json.loads(
        result.raw_payload
    )

    assert (
        raw_payload["requester"]
        == payload[
            "response"
        ][
            "cover"
        ][
            "requester"
        ]
    )

    assert (
        raw_payload[
            "requester"
        ][
            "requester_MP_id"
        ]
        is None
    )


def test_raw_payload_does_not_modify_original_submission():
    payload = create_payload()

    payload[
        "response"
    ][
        "cover"
    ][
        "requester"
    ] = {
        "company": "Requester Kft.",
        "requester_MP_id": None,
        "tax_number": "12345678",
    }

    assert (
        "requester"
        not in payload
    )

    (
        SubmissionPersistenceMapper
        .map_submission(
            submission_payload=payload,
            batch_id="BATCH_TEST",
            relation_id=274,
        )
    )

    assert (
        "requester"
        not in payload
    )

def test_normalize_tax_number_preserves_country_prefix():
    result = (
        SubmissionPersistenceMapper
        .normalize_tax_number(
            "IT02228260200"
        )
    )

    assert result == "IT02228260200"


def test_normalize_tax_number_removes_foreign_formatting():
    result = (
        SubmissionPersistenceMapper
        .normalize_tax_number(
            "CHE-153.922.051"
        )
    )

    assert result == "CHE153922051"


def test_create_external_supplier_key_preserves_country_prefix():
    result = (
        SubmissionPersistenceMapper
        .create_external_supplier_key(
            "IT02228260200"
        )
    )

    assert result == "SUP_IT02228260200"


def test_create_respondent_id_preserves_country_prefix():
    result = (
        SubmissionPersistenceMapper
        .create_respondent_id(
            "IT02228260200",
            "2025",
        )
    )

    assert (
        result
        == "RESP_IT02228260200_2025"
    )