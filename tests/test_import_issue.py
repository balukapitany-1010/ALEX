import pytest

from alex.esg.services.import_issue import (
    ImportIssue,
    ImportIssueSeverity,
)


def test_import_issue_can_be_created():
    issue = ImportIssue(
        severity=ImportIssueSeverity.ERROR,
        code="SUPPLIER_TAX_NUMBER_MISSING",
        message="supplier tax number is missing",
    )

    assert (
        issue.severity
        is ImportIssueSeverity.ERROR
    )

    assert (
        issue.code
        == "SUPPLIER_TAX_NUMBER_MISSING"
    )


def test_import_issue_rejects_empty_code():
    with pytest.raises(
        ValueError,
        match="code cannot be empty",
    ):
        ImportIssue(
            severity=ImportIssueSeverity.ERROR,
            code="",
            message="hiba",
        )


def test_import_issue_rejects_empty_message():
    with pytest.raises(
        ValueError,
        match="message cannot be empty",
    ):
        ImportIssue(
            severity=ImportIssueSeverity.WARNING,
            code="TEST",
            message="",
        )
