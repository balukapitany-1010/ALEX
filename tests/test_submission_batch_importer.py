from alex.esg.services.submission_batch_importer import (
    SubmissionBatchImporter,
)


def test_batch_importer_inspects_valid_submission():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": None,
                    "respondent_MP_id": None,
                    "org_size": "Large",
                    "submitted_at": (
                        "2026-02-12T11:54:29Z"
                    ),
                    "cover": {
                        "supplier": {
                            "company": "Beszállító Kft.",
                            "tax_number": (
                                "11111111-2-41"
                            ),
                            "period": "2026-Q1",
                        },
                        "requester": {
                            "company": "ABC Zrt.",
                            "tax_number": (
                                "22222222-2-41"
                            ),
                            "requester_MP_id": None,
                        },
                    },
                    "questions": [],
                }
            }
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    assert result.spec_version == "2.1"
    assert result.batch_id == "TEST_BATCH"

    assert result.total_count == 1
    assert result.valid_count == 1
    assert result.invalid_count == 0

    assert result.items[0].is_valid is True
    assert result.items[0].errors == ()

def test_batch_importer_reports_missing_header_data():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": None,
                    "respondent_MP_id": None,
                    "org_size": None,
                    "submitted_at": (
                        "2026-02-12T11:54:29Z"
                    ),
                    "cover": {
                        "supplier": {
                            "company": (
                                "Minta Beszállító Kft."
                            ),
                            "tax_number": "",
                            "period": "",
                        },
                        "requester": {
                            "company": "",
                            "tax_number": "",
                            "requester_MP_id": None,
                        },
                    },
                    "questions": [],
                }
            }
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    assert result.total_count == 1
    assert result.valid_count == 0
    assert result.invalid_count == 1

    item = result.items[0]

    assert item.is_valid is False

    assert (
        "supplier tax number is missing"
        in item.errors
    )

    assert (
        "requester company is missing"
        in item.errors
    )

    assert (
        "requester tax number is missing"
        in item.errors
    )

    assert (
        "submission period is missing"
        in item.errors
    )

def test_batch_importer_continues_after_invalid_submission():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {}
            },
            {
                "response": {
                    "respondent_id": None,
                    "respondent_MP_id": None,
                    "org_size": "Large",
                    "submitted_at": (
                        "2026-02-12T11:54:29Z"
                    ),
                    "cover": {
                        "supplier": {
                            "company": "Beszállító Kft.",
                            "tax_number": (
                                "11111111-2-41"
                            ),
                            "period": "2026-Q1",
                        },
                        "requester": {
                            "company": "ABC Zrt.",
                            "tax_number": (
                                "22222222-2-41"
                            ),
                            "requester_MP_id": None,
                        },
                    },
                    "questions": [],
                }
            },
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    assert result.total_count == 2
    assert result.valid_count == 1
    assert result.invalid_count == 1

    assert result.items[0].is_valid is False
    assert result.items[1].is_valid is True