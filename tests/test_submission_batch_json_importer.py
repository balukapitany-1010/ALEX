from alex.esg.domain.question import Question
from alex.esg.domain.question_category import (
    QuestionCategory,
)
from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.mappers.submission_header_mapper import (
    SubmissionHeaderMapper,
)
from alex.esg.services.company_service import (
    CompanyService,
)
from alex.esg.services.submission_batch_importer import (
    SubmissionBatchImporter,
)
from alex.esg.services.submission_batch_json_importer import (
    SubmissionBatchJsonImporter,
)
from alex.esg.services.submission_builder_service import (
    SubmissionBuilderService,
)
from alex.esg.services.submission_definition_validator import (
    SubmissionDefinitionValidator,
)
from alex.esg.services.submission_import_service import (
    SubmissionImportService,
)
from alex.esg.services.submission_json_importer import (
    SubmissionJsonImporter,
)
from alex.esg.services.submission_party_resolver import (
    SubmissionPartyResolver,
)
from alex.esg.services.submission_relation_resolver import (
    SubmissionRelationResolver,
)
from alex.esg.services.submission_submitter_resolver import (
    SubmissionSubmitterResolver,
)
from alex.esg.services.supplier_service import (
    SupplierService,
)
from alex.esg.services.supply_chain_relation_service import (
    SupplyChainRelationService,
)


def _create_environment():
    company_service = CompanyService()
    supplier_service = SupplierService()

    relation_service = (
        SupplyChainRelationService()
    )

    party_resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    relation_resolver = (
        SubmissionRelationResolver(
            relation_service=relation_service,
        )
    )

    submitter_resolver = (
        SubmissionSubmitterResolver(
            company_service=company_service,
        )
    )

    builder = SubmissionBuilderService(
        party_resolver=party_resolver,
        relation_resolver=relation_resolver,
        submitter_resolver=submitter_resolver,
    )

    submission_importer = SubmissionJsonImporter(
        header_mapper=SubmissionHeaderMapper(),
        builder=builder,
        submission_import_service=(
            SubmissionImportService()
        ),
    )

    batch_importer = SubmissionBatchJsonImporter(
        batch_inspector=SubmissionBatchImporter(),
        definition_validator=(
            SubmissionDefinitionValidator()
        ),
        submission_importer=submission_importer,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="TEST_ID",
        question_code="E1",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.TEXT,
    )

    return (
        batch_importer,
        questionnaire,
        definition,
        company_service,
        supplier_service,
        relation_service,
    )


def _create_submission_data(
    *,
    supplier_name: str = "Beszállító Kft.",
    supplier_tax_number: str = (
        "11111111-2-41"
    ),
):
    return {
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
                    "company": supplier_name,
                    "tax_number": (
                        supplier_tax_number
                    ),
                    "period": "2026-Q1",
                },
                "requester": {
                    "company": "Kötelezett Zrt.",
                    "tax_number": (
                        "22222222-2-41"
                    ),
                    "requester_MP_id": "REQ-1",
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


def test_batch_importer_imports_valid_submissions():
    (
        importer,
        questionnaire,
        definition,
        _,
        _,
        _,
    ) = _create_environment()

    batch_data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            _create_submission_data(),
            _create_submission_data(),
        ],
    }

    result = importer.import_batch(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.total_count == 2
    assert result.imported_count == 2
    assert result.failed_count == 0

    assert len(result.submissions) == 2

    assert all(
        len(submission.answers) == 1
        for submission in result.submissions
    )

    assert result.errors == ()


def test_batch_importer_continues_after_invalid_submission():
    (
        importer,
        questionnaire,
        definition,
        _,
        _,
        _,
    ) = _create_environment()

    batch_data = {
        "spec_version": "2.1",
        "batch_id": "TEST_BATCH",
        "submissions": [
            _create_submission_data(
                supplier_tax_number=""
            ),
            _create_submission_data(),
        ],
    }

    result = importer.import_batch(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.total_count == 2

    assert result.imported_count == 1
    assert result.failed_count == 1

    assert result.items[0].submission is None

    assert (
        result.items[1].submission
        is not None
    )

    assert any(
        issue.code
        == "SUPPLIER_TAX_NUMBER_MISSING"
        for issue in result.items[0].errors
    )


def test_batch_importer_stops_all_on_version_mismatch():
    (
        importer,
        questionnaire,
        definition,
        company_service,
        supplier_service,
        relation_service,
    ) = _create_environment()

    batch_data = {
        "spec_version": "2.0",
        "batch_id": "TEST_BATCH",
        "submissions": [
            _create_submission_data(),
            _create_submission_data(),
        ],
    }

    result = importer.import_batch(
        batch_data,
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert result.total_count == 2
    assert result.imported_count == 0
    assert result.failed_count == 2

    assert any(
        issue.code
        == "QUESTIONNAIRE_VERSION_MISMATCH"
        for issue in result.errors
    )

    assert (
        company_service.list_companies()
        == ()
    )

    assert (
        supplier_service.list_suppliers()
        == ()
    )

    assert (
        relation_service.list_relations()
        == ()
    )