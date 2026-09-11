from alex.esg.infrastructure.repositories.mssql_submission_import_context_reader import MssqlSubmissionImportContextReader

def test_business_identifiers_match_hungarian_vat_and_domestic_tax_number():
    assert (MssqlSubmissionImportContextReader.business_identifiers_match(
            "HU13136062",
            "13136062-2-44",
        )
        is True
    )


def test_business_identifiers_match_hungarian_tax_number_reverse_direction():
    assert (MssqlSubmissionImportContextReader.business_identifiers_match(
            "13136062-2-44",
            "HU13136062",
        )
        is True
    )


def test_business_identifiers_match_exact_foreign_identifier():
    assert (MssqlSubmissionImportContextReader.business_identifiers_match(
            "DE317264370",
            "DE317264370",
        )
        is True
    )


def test_business_identifiers_do_not_match_different_hungarian_taxpayers():
    assert (MssqlSubmissionImportContextReader.business_identifiers_match(
            "HU13136062",
            "13136063-2-44",
        )
        is False
    )