from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation
from alex.esg.services.submission_batch_json_importer import (
    SubmissionBatchJsonImportResult,
    SubmissionBatchJsonItemResult,
)
from alex.esg.services.submission_batch_registration_service import SubmissionBatchRegistrationService
from alex.esg.services.submission_service import SubmissionService


def _create_submission():
    requester = Company(
        name="Kötelezett Zrt.",
        tax_number="11111111-2-41",
        country="HU",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-41",
        country="HU",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    return Submission(
        relation=relation,
        submitter=None,
        questionnaire=questionnaire,
        period="2026-Q1",
    )


def test_registration_service_adds_imported_submissions():
    submission_service = SubmissionService()

    registration_service = (
        SubmissionBatchRegistrationService(
            submission_service=submission_service,
        )
    )

    submission1 = _create_submission()
    submission2 = _create_submission()

    result = SubmissionBatchJsonImportResult(
        spec_version="2.1",
        batch_id="TEST_BATCH",
        items=(
            SubmissionBatchJsonItemResult(
                index=0,
                submission=submission1,
                issues=(),
            ),
            SubmissionBatchJsonItemResult(
                index=1,
                submission=submission2,
                issues=(),
            ),
        ),
        issues=(),
    )

    registered = (
        registration_service.register_import_result(
            result
        )
    )

    assert len(registered) == 2

    assert (submission_service.list_submissions() == (submission1, submission2,))