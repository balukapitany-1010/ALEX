import pytest
from datetime import datetime
from alex.esg.domain.attachment import Attachment
from alex.esg.domain.company import Company
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.submission import Submission
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


def create_submission() -> tuple[Submission, Questionnaire]:
    requester = Company(
        name="Megrendelő Kft.",
        tax_number="11111111-1-11",
    )

    supplier = Supplier(
        name="Beszállító Kft.",
        tax_number="22222222-2-22",
    )

    relation = SupplyChainRelation(
        requester=requester,
        supplier=supplier,
    )

    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    submission = Submission(
        relation=relation,
        submitter=supplier,
        questionnaire=questionnaire,
        period="2026-Q2",
    )

    return submission, questionnaire


def create_definition(
    questionnaire: Questionnaire,
) -> QuestionDefinition:
    question = Question(
        question_id="3737695",
        question_code="E1",
    )

    return QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )


def test_attachment_belongs_to_submission():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.submission is submission
    assert attachment.question_definition is None


def test_attachment_can_belong_to_question():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    attachment = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.submission is submission
    assert attachment.question_definition is definition


def test_attachment_generates_attachment_id():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert isinstance(attachment.attachment_id, str)
    assert len(attachment.attachment_id) > 0


def test_attachment_rejects_invalid_submission():
    with pytest.raises(TypeError):
        Attachment(
            submission="Nem Submission objektum",
        )


def test_attachment_rejects_invalid_question_definition():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            question_definition="E1",
        )

def test_attachment_has_file_name():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.file_name == "teszt.pdf"


def test_attachment_rejects_empty_file_name():
    submission, _ = create_submission()

    with pytest.raises(ValueError):
        Attachment(
            submission=submission,
            file_name="",
            storage_reference="ATT_TEST_001",
        )


def test_attachment_rejects_invalid_file_name():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            file_name=123,
        )


def test_attachment_file_name_cannot_be_changed_directly():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    with pytest.raises(AttributeError):
        attachment.file_name = "masik.pdf"


def test_attachment_has_storage_reference():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.storage_reference == "ATT_TEST_001"


def test_attachment_rejects_empty_storage_reference():
    submission, _ = create_submission()

    with pytest.raises(ValueError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference="",
        )


def test_attachment_rejects_invalid_storage_reference():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference=123,
        )


def test_attachment_storage_reference_cannot_be_changed_directly():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    with pytest.raises(AttributeError):
        attachment.storage_reference = "ATT_TEST_002"

def test_attachment_can_have_content_type():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
        content_type="application/pdf",
    )

    assert attachment.content_type == "application/pdf"


def test_attachment_content_type_can_be_none():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.content_type is None


def test_attachment_rejects_invalid_content_type():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference="ATT_TEST_001",
            content_type=123,
        )


def test_attachment_content_type_cannot_be_changed_directly():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
        content_type="application/pdf",
    )

    with pytest.raises(AttributeError):
        attachment.content_type = "image/png"

def test_attachment_can_have_file_size():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
        file_size=2048,
    )

    assert attachment.file_size == 2048


def test_attachment_file_size_can_be_none():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.file_size is None


def test_attachment_rejects_invalid_file_size():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference="ATT_TEST_001",
            file_size="2048",
        )


def test_attachment_rejects_boolean_file_size():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference="ATT_TEST_001",
            file_size=True,
        )


def test_attachment_rejects_negative_file_size():
    submission, _ = create_submission()

    with pytest.raises(ValueError):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            storage_reference="ATT_TEST_001",
            file_size=-1,
        )


def test_attachment_file_size_cannot_be_changed_directly():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
        file_size=2048,
    )

    with pytest.raises(AttributeError):
        attachment.file_size = 4096

def test_attachment_has_created_at():
    submission, _ = create_submission()
    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )
    assert attachment.created_at is not None
    assert isinstance(attachment.created_at, datetime)

def test_attachment_created_at_cannot_be_changed_directly():
    submission, _ = create_submission()
    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )
    original_created_at = attachment.created_at
    with pytest.raises(AttributeError):
        attachment.created_at = datetime.now()

    assert attachment.created_at == original_created_at

def test_attachment_rejects_question_definition_from_different_questionnaire():
    submission, _ = create_submission()

    other_questionnaire = Questionnaire(
        questionnaire_code = "SZTFH",
        spec_version = "2.2",
        locale = "hu",
    )
    definition = create_definition(other_questionnaire)
    with pytest.raises(ValueError, match = "question_definition must belong to the same questionnaire",):
        Attachment(
            submission=submission,
            file_name="teszt.pdf",
            question_definition=definition,
            storage_reference="ATT_TEST_001",
        )

def test_attachment_accepts_question_definition_from_logically_same_questionnaire():
    submission, _ = create_submission()

    same_questionnaire = Questionnaire(
        questionnaire_code = "SZTFH",
        spec_version = "2.1",
        locale = "hu",
    )
    definition = create_definition(same_questionnaire)
    attachment = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )
    assert attachment.question_definition is definition

def test_submission_has_no_attachments_by_default():
    submission, _ = create_submission()

    assert submission.attachments == ()


def test_submission_can_add_attachment():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    assert submission.attachments == (attachment,)


def test_submission_rejects_invalid_attachment():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        submission.add_attachment("not an attachment")


def test_submission_rejects_attachment_from_other_submission():
    submission, _ = create_submission()
    other_submission, _ = create_submission()

    attachment = Attachment(
        submission=other_submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    with pytest.raises(
        ValueError,
        match="attachment must belong to this Submission",
    ):
        submission.add_attachment(attachment)


def test_submission_rejects_same_attachment_twice():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    with pytest.raises(
        ValueError,
        match="attachment already exists",
    ):
        submission.add_attachment(attachment)


def test_submission_can_get_attachment_by_id():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    result = submission.get_attachment(
        attachment.attachment_id
    )

    assert result is attachment


def test_submission_get_attachment_returns_none_when_not_found():
    submission, _ = create_submission()

    assert (
        submission.get_attachment("missing-attachment")
        is None
    )


def test_submission_has_attachment():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    assert submission.has_attachment(
        attachment.attachment_id
    ) is True

    assert submission.has_attachment(
        "missing-attachment"
    ) is False

def test_submission_attachments_returns_only_submission_level_attachments():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    submission_attachment = Attachment(
        submission=submission,
        file_name="teljes_bekuldes.pdf",
        storage_reference="ATT_SUBMISSION_001",
    )

    question_attachment = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="E1_igazolas.pdf",
        storage_reference="ATT_QUESTION_001",
    )

    submission.add_attachment(submission_attachment)
    submission.add_attachment(question_attachment)

    assert submission.submission_attachments == (
        submission_attachment,
    )


def test_question_attachments_returns_only_question_level_attachments():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    submission_attachment = Attachment(
        submission=submission,
        file_name="teljes_bekuldes.pdf",
        storage_reference="ATT_SUBMISSION_001",
    )

    question_attachment = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="E1_igazolas.pdf",
        storage_reference="ATT_QUESTION_001",
    )

    submission.add_attachment(submission_attachment)
    submission.add_attachment(question_attachment)

    assert submission.question_attachments == (
        question_attachment,
    )

def test_submission_can_get_attachments_for_question():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    attachment1 = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="E1_igazolas_1.pdf",
        storage_reference="ATT_E1_001",
    )

    attachment2 = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="E1_igazolas_2.pdf",
        storage_reference="ATT_E1_002",
    )

    submission.add_attachment(attachment1)
    submission.add_attachment(attachment2)

    result = submission.get_attachments_for_question(
        definition.question.question_id
    )

    assert result == (
        attachment1,
        attachment2,
    )

def test_get_attachments_for_question_returns_empty_tuple_when_none_exist():
    submission, _ = create_submission()

    result = submission.get_attachments_for_question(
        "missing-question"
    )

    assert result == ()

def test_get_attachments_for_question_rejects_invalid_question_id():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        submission.get_attachments_for_question(123)


def test_get_attachments_for_question_rejects_empty_question_id():
    submission, _ = create_submission()

    with pytest.raises(ValueError):
        submission.get_attachments_for_question("")

def test_attachment_id_cannot_be_changed_directly():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    original_attachment_id = attachment.attachment_id

    with pytest.raises(AttributeError):
        attachment.attachment_id = "new-id"

    assert attachment.attachment_id == original_attachment_id


def test_attachment_submission_cannot_be_changed_directly():
    submission, _ = create_submission()
    other_submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    with pytest.raises(AttributeError):
        attachment.submission = other_submission

    assert attachment.submission is submission


def test_attachment_question_definition_cannot_be_changed_directly():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    attachment = Attachment(
        submission=submission,
        question_definition=definition,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    other_definition = QuestionDefinition(
        question=Question(
            question_id="OTHER",
            question_code="E2",
        ),
        questionnaire=questionnaire,
        title="Másik kérdés",
        category=QuestionCategory.E,
        subject="Környezeti Fenntarthatóság",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU/EGT/Switzerland"],
        topic="Energia",
        question_type=QuestionType.TEXT,
    )

    with pytest.raises(AttributeError):
        attachment.question_definition = other_definition

    assert attachment.question_definition is definition

def test_submission_level_attachment_cannot_be_reassigned_to_question():
    submission, questionnaire = create_submission()

    definition = create_definition(questionnaire)

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    assert attachment.question_definition is None

    with pytest.raises(AttributeError):
        attachment.question_definition = definition

    assert attachment.question_definition is None

def test_submission_can_remove_attachment():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    removed = submission.remove_attachment(
        attachment.attachment_id
    )

    assert removed is attachment
    assert submission.attachments == ()
    assert submission.has_attachment(
        attachment.attachment_id
    ) is False

def test_remove_attachment_removes_only_requested_attachment():
    submission, _ = create_submission()

    attachment1 = Attachment(
        submission=submission,
        file_name="elso.pdf",
        storage_reference="ATT_TEST_001",
    )

    attachment2 = Attachment(
        submission=submission,
        file_name="masodik.pdf",
        storage_reference="ATT_TEST_002",
    )

    submission.add_attachment(attachment1)
    submission.add_attachment(attachment2)

    submission.remove_attachment(
        attachment1.attachment_id
    )

    assert submission.attachments == (
        attachment2,
    )
def test_submission_rejects_removing_missing_attachment():
    submission, _ = create_submission()

    with pytest.raises(
        ValueError,
        match="attachment does not exist",
    ):
        submission.remove_attachment(
            "missing-attachment"
        )
def test_remove_attachment_rejects_invalid_attachment_id():
    submission, _ = create_submission()

    with pytest.raises(TypeError):
        submission.remove_attachment(123)
def test_remove_attachment_rejects_empty_attachment_id():
    submission, _ = create_submission()

    with pytest.raises(ValueError):
        submission.remove_attachment("")
def test_remove_attachment_updates_submission_updated_at():
    submission, _ = create_submission()

    attachment = Attachment(
        submission=submission,
        file_name="teszt.pdf",
        storage_reference="ATT_TEST_001",
    )

    submission.add_attachment(attachment)

    previous_updated_at = submission.updated_at

    submission.remove_attachment(
        attachment.attachment_id
    )

    assert submission.updated_at >= previous_updated_at