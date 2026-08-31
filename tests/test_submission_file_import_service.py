import json

from alex.esg.mappers.questionnaire_definition_mapper import  QuestionnaireDefinitionMapper
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderMapper
from alex.esg.services.company_service import CompanyService
from alex.esg.services.json_import_service import JsonImportService
from alex.esg.services.submission_batch_importer import SubmissionBatchImporter
from alex.esg.services.submission_batch_json_importer import SubmissionBatchJsonImporter
from alex.esg.services.submission_batch_registration_service import SubmissionBatchRegistrationService
from alex.esg.services.submission_builder_service import SubmissionBuilderService
from alex.esg.services.submission_definition_validator import SubmissionDefinitionValidator
from alex.esg.services.submission_file_import_service import SubmissionFileImportService

from alex.esg.services.submission_import_service import SubmissionImportService
from alex.esg.services.submission_json_importer import SubmissionJsonImporter
from alex.esg.services.submission_party_resolver import SubmissionPartyResolver
from alex.esg.services.submission_relation_resolver import SubmissionRelationResolver
from alex.esg.services.submission_service import SubmissionService
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver
from alex.esg.services.supplier_service import SupplierService
from alex.esg.services.supply_chain_relation_service import SupplyChainRelationService


def _create_service():
    company_service = CompanyService()
    supplier_service = SupplierService()
    relation_service = (SupplyChainRelationService())
    submission_service = SubmissionService()

    party_resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    relation_resolver = (SubmissionRelationResolver(relation_service=relation_service))

    submitter_resolver = (SubmissionSubmitterResolver(company_service=company_service))

    builder = SubmissionBuilderService(
        party_resolver=party_resolver,
        relation_resolver=relation_resolver,
        submitter_resolver=submitter_resolver,
    )

    single_importer = SubmissionJsonImporter(
        header_mapper=SubmissionHeaderMapper(),
        builder=builder,
        submission_import_service=(SubmissionImportService()),
    )

    batch_importer = SubmissionBatchJsonImporter(
        batch_inspector=SubmissionBatchImporter(),
        definition_validator=(SubmissionDefinitionValidator()),
        submission_importer=single_importer,
    )

    registration_service = (SubmissionBatchRegistrationService(submission_service=submission_service))

    service = SubmissionFileImportService(
        json_service=JsonImportService(),
        definition_mapper=(QuestionnaireDefinitionMapper()),
        batch_importer=batch_importer,
        registration_service=(registration_service),
    )

    return service, submission_service

def _write_test_files(
    tmp_path,
    *,
    definition_version="2.1",
    submission_version="2.1",
):
    definition_data = {
        "spec_version": definition_version,
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E1",
                        "title": "Teszt kérdés",
                        "type": "text",
                        "category": "E",
                        "ID": "TEST_ID",
                        "topic": "Teszt",
                        "organization_size": [
                            "Large"
                        ],
                        "GeographicalRelevance": [
                            "HU"
                        ],
                        "organization": "SZTFH",
                    }
                ]
            }
        ],
    }

    submission_data = {
        "spec_version": submission_version,
        "batch_id": "TEST_BATCH",
        "submissions": [
            {
                "response": {
                    "respondent_id": "RESP-1",
                    "respondent_MP_id": "MP-1",
                    "organization": None,
                    "org_size": "Large",
                    "submitted_at": (
                        "2026-02-12T11:54:29Z"
                    ),
                    "cover": {
                        "supplier": {
                            "company": (
                                "Beszállító Kft."
                            ),
                            "tax_number": (
                                "11111111-2-41"
                            ),
                            "period": "2026-Q1",
                        },
                        "requester": {
                            "company": (
                                "Kötelezett Zrt."
                            ),
                            "tax_number": (
                                "22222222-2-41"
                            ),
                            "requester_MP_id": (
                                "REQ-1"
                            ),
                        },
                        "submitter_auditor": {
                            "company": "",
                            "tax_number": "",
                            "representative": "",
                            "phone": "",
                            "email": "",
                            "period": "",
                        },
                    },
                    "questions": [
                        {
                            "id": "TEST_ID",
                            "question_id": "E1",
                            "fields": [
                                {
                                    "type": "text",
                                    "values": [
                                        {
                                            "value": (
                                                "Teszt válasz"
                                            )
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            }
        ],
    }

    definition_file = (
        tmp_path
        / "definition.json"
    )

    submission_file = (
        tmp_path
        / "submission.json"
    )

    definition_file.write_text(
        json.dumps(
            definition_data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    submission_file.write_text(
        json.dumps(
            submission_data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return (
        definition_file,
        submission_file,
    )

def test_file_import_registers_submission(
    tmp_path,
):
    service, submission_service = (
        _create_service()
    )

    (
        definition_file,
        submission_file,
    ) = _write_test_files(
        tmp_path
    )

    result = service.import_files(
        definition_file=definition_file,
        submission_file=submission_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert result.is_successful is True

    assert result.imported_count == 1
    assert result.failed_count == 0

    assert len(result.question_definitions) == 1

    assert len(result.registered_submissions) == 1

    submissions = (submission_service.list_submissions())

    assert len(submissions) == 1

    submission = submissions[0]

    assert submission.period == "2026-Q1"

    assert len(submission.answers) == 1

    assert (submission.answers[0].values[0].text_value  == "Teszt válasz")

def test_file_import_does_not_register_wrong_version(tmp_path):
    service, submission_service = (_create_service())

    (
        definition_file,
        submission_file,
    ) = _write_test_files(
        tmp_path,
        definition_version="2.0",
        submission_version="2.1",
    )

    result = service.import_files(
        definition_file=definition_file,
        submission_file=submission_file,
        questionnaire_code="SZTFH-ESG",
    )

    assert result.is_successful is False

    assert result.imported_count == 0

    assert (submission_service.list_submissions() == ())

    assert any( issue.code == "QUESTIONNAIRE_VERSION_MISMATCH" for issue in result.batch_result.errors)