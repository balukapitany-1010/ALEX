from alex.esg.services.submission_batch_importer import (
    SubmissionBatchImporter,
)
from pathlib import Path

from alex.esg.services.json_import_service import (
    JsonImportService,
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

    error_codes = {
        issue.code
        for issue in item.errors
    }

    assert (
        "SUPPLIER_TAX_NUMBER_MISSING"
        in error_codes
    )

    assert (
        "REQUESTER_COMPANY_MISSING"
        in error_codes
    )

    assert (
        "REQUESTER_TAX_NUMBER_MISSING"
        in error_codes
    )

    assert (
        "SUBMISSION_PERIOD_MISSING"
        in error_codes
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

def test_batch_importer_inspects_real_2_1_sample():
    file_path = (
        Path(__file__).parent
        / "data"
        / "Sztfh_kerdoiv_2_1_valaszminta.json"
    )

    json_service = JsonImportService()
    importer = SubmissionBatchImporter()

    data = json_service.load_file(
        file_path
    )

    result = importer.inspect_batch(
        data
    )

    assert result.spec_version == "2.1"

    assert (
        result.batch_id
        == "SZTFH_BATCH_CB30205155"
    )

    assert result.total_count > 0

    first_item = result.items[0]

    assert first_item.header is not None
    assert first_item.is_valid is False

    assert (
        first_item.header.supplier_company
        == "Minta Beszállító Kft."
    )

    error_codes = {
        issue.code
        for issue in first_item.errors
    }

    assert (
        "SUPPLIER_TAX_NUMBER_MISSING"
        in error_codes
    )

    assert (
        "REQUESTER_COMPANY_MISSING"
        in error_codes
    )

    assert (
        "REQUESTER_TAX_NUMBER_MISSING"
        in error_codes
    )

    assert (
        "SUBMISSION_PERIOD_MISSING"
        in error_codes
    )

    warning_codes = {
        issue.code
        for issue in first_item.warnings
    }

    assert (
        "RESPONDENT_ID_MISSING"
        in warning_codes
    )

    assert (
        "RESPONDENT_MP_ID_MISSING"
        in warning_codes
    )

    assert (
        "ORG_SIZE_MISSING"
        in warning_codes
    )
    assert len(first_item.errors) == 4
    assert len(first_item.warnings) == 3

def test_batch_importer_reports_duplicate_question_id():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
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
                            "requester_MP_id": "REQ-1",
                        },
                    },
                    "questions": [
                        {
                            "id": "3737695",
                            "question_id": "E1",
                            "fields": [],
                        },
                        {
                            "id": "3737695",
                            "question_id": "E2",
                            "fields": [],
                        },
                    ],
                }
            }
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    item = result.items[0]

    assert item.is_valid is False

    assert any(
        issue.code
        == "DUPLICATE_QUESTION_ID"
        for issue in item.errors
    )

def test_duplicate_question_code_is_warning():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
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
                            "requester_MP_id": "REQ-1",
                        },
                    },
                    "questions": [
                        {
                            "id": "TEST_1",
                            "question_id": "E1",
                            "fields": [],
                        },
                        {
                            "id": "TEST_2",
                            "question_id": "E1",
                            "fields": [],
                        },
                    ],
                }
            }
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    item = result.items[0]

    assert item.is_valid is True

    assert any(
        issue.code
        == "DUPLICATE_QUESTION_CODE"
        for issue in item.warnings
    )

def test_batch_importer_reports_invalid_question_fields():
    data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
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
                            "requester_MP_id": "REQ-1",
                        },
                    },
                    "questions": [
                        {
                            "id": "3737695",
                            "question_id": "E1",
                            "fields": None,
                        }
                    ],
                }
            }
        ],
    }

    importer = SubmissionBatchImporter()

    result = importer.inspect_batch(
        data
    )

    item = result.items[0]

    assert item.is_valid is False

    assert any(
        issue.code
        == "QUESTION_FIELDS_INVALID"
        for issue in item.errors
    )