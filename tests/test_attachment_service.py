from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.services.attachment_service import (
    AttachmentService,
)


def _create_submission() -> Submission:
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


def test_attachment_service_creates_attachment():
    service = AttachmentService()

    submission = _create_submission()

    attachment = service.create_attachment(
        submission=submission,
        file_name="jelentes.pdf",
        storage_reference=(
            "documents/jelentes.pdf"
        ),
        content_type="application/pdf",
        file_size=12345,
    )

    assert (
        attachment.submission
        is submission
    )

    assert (
        attachment.file_name
        == "jelentes.pdf"
    )

    assert (
        attachment.storage_reference
        == "documents/jelentes.pdf"
    )

    assert submission.attachments == (
        attachment,
    )


def test_attachment_service_lists_submission_attachments():
    service = AttachmentService()

    submission = _create_submission()

    attachment1 = service.create_attachment(
        submission=submission,
        file_name="a.pdf",
        storage_reference="documents/a.pdf",
    )

    attachment2 = service.create_attachment(
        submission=submission,
        file_name="b.pdf",
        storage_reference="documents/b.pdf",
    )

    result = service.list_for_submission(
        submission
    )

    assert result == (
        attachment1,
        attachment2,
    )


def test_attachment_service_gets_attachment_by_id():
    service = AttachmentService()

    submission = _create_submission()

    attachment = service.create_attachment(
        submission=submission,
        file_name="jelentes.pdf",
        storage_reference=(
            "documents/jelentes.pdf"
        ),
    )

    result = service.get_by_id(
        submission=submission,
        attachment_id=(
            attachment.attachment_id
        ),
    )

    assert result is attachment


def test_attachment_service_removes_attachment():
    service = AttachmentService()

    submission = _create_submission()

    attachment = service.create_attachment(
        submission=submission,
        file_name="jelentes.pdf",
        storage_reference=(
            "documents/jelentes.pdf"
        ),
    )

    removed = service.remove_attachment(
        submission=submission,
        attachment_id=(
            attachment.attachment_id
        ),
    )

    assert removed is attachment

    assert submission.attachments == ()