import pytest

from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderMapper
from alex.esg.services.company_service import CompanyService
from alex.esg.services.submission_builder_service import SubmissionBuilderService
from alex.esg.services.submission_import_service import  SubmissionImportService
from alex.esg.services.submission_json_importer import SubmissionJsonImporter
from alex.esg.services.submission_party_resolver import SubmissionPartyResolver
from alex.esg.services.submission_relation_resolver import SubmissionRelationResolver
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver
from alex.esg.services.supplier_service import SupplierService
from alex.esg.services.supply_chain_relation_service import SupplyChainRelationService


def _create_importer():
    company_service = CompanyService()
    supplier_service = SupplierService()
    relation_service = SupplyChainRelationService()

    party_resolver = SubmissionPartyResolver(
        company_service=company_service,
        supplier_service=supplier_service,
    )

    relation_resolver = SubmissionRelationResolver(
        relation_service=relation_service,
    )

    submitter_resolver = SubmissionSubmitterResolver(
        company_service=company_service,
    )

    builder = SubmissionBuilderService(
        party_resolver=party_resolver,
        relation_resolver=relation_resolver,
        submitter_resolver=submitter_resolver,
    )

    importer = SubmissionJsonImporter(
        header_mapper=SubmissionHeaderMapper(),
        builder=builder,
        submission_import_service=(
            SubmissionImportService()
        ),
    )

    return (
        importer,
        company_service,
        supplier_service,
        relation_service,
    )


def _create_questionnaire():
    return Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )


def _create_definition(
    questionnaire: Questionnaire,
) -> QuestionDefinition:
    question = Question(
        question_id="TEST_ID",
        question_code="E1",
    )

    return QuestionDefinition(
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


def _create_submission_data():
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
                    "company": "Beszállító Kft.",
                    "tax_number": "11111111-2-41",
                    "period": "2026-Q1",
                },
                "requester": {
                    "company": "Kötelezett Zrt.",
                    "tax_number": "22222222-2-41",
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
                                    "value": "Teszt válasz"
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    }


def test_json_importer_builds_complete_submission():
    (
        importer,
        company_service,
        supplier_service,
        relation_service,
    ) = _create_importer()

    questionnaire = _create_questionnaire()

    definition = _create_definition(questionnaire)

    submission = importer.import_submission(
        _create_submission_data(),
        spec_version="2.1",
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert submission.period == "2026-Q1"

    assert (submission.organization_size == "Large")

    assert submission.submitter is None

    assert (submission.relation.requester.name == "Kötelezett Zrt.")

    assert (submission.relation.supplier.name == "Beszállító Kft.")

    assert len(submission.answers) == 1

    answer = submission.answers[0]

    assert (answer.question_definition is definition)

    assert len(answer.values) == 1

    assert (answer.values[0].text_value == "Teszt válasz")

    assert answer.is_answered is True

    assert len(company_service.list_companies()) == 1

    assert len(supplier_service.list_suppliers()) == 1

    assert len(relation_service.list_relations()) == 1

def test_json_importer_rejects_version_before_creating_domain_objects():
    (
        importer,
        company_service,
        supplier_service,
        relation_service,
    ) = _create_importer()

    questionnaire = _create_questionnaire()

    definition = _create_definition(questionnaire)

    with pytest.raises(
        ValueError,
        match="does not match submission version",
    ):
        importer.import_submission(
            _create_submission_data(),
            spec_version="2.0",
            questionnaire=questionnaire,
            question_definitions=(
                definition,
            ),
        )

    assert (company_service.list_companies()== ())

    assert (supplier_service.list_suppliers()== ())

    assert (relation_service.list_relations()== ())

def test_json_importer_reuses_existing_parties_and_relation():
    (
        importer,
        company_service,
        supplier_service,
        relation_service,
    ) = _create_importer()

    questionnaire = _create_questionnaire()

    definition = _create_definition(questionnaire)

    submission1 = importer.import_submission(
        _create_submission_data(),
        spec_version="2.1",
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    submission2 = importer.import_submission(
        _create_submission_data(),
        spec_version="2.1",
        questionnaire=questionnaire,
        question_definitions=(
            definition,
        ),
    )

    assert (submission1 is not submission2)

    assert (submission1.relation is submission2.relation)

    assert len(company_service.list_companies()) == 1

    assert len(supplier_service.list_suppliers()) == 1

    assert len(relation_service.list_relations()) == 1

    assert len(submission1.answers) == 1
    assert len(submission2.answers) == 1