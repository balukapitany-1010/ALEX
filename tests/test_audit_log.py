from datetime import datetime

import pytest

from alex.esg.domain.audit_action import AuditAction
from alex.esg.domain.audit_log import AuditLog


def test_audit_log_stores_event_data():
    audit_log = AuditLog(
        entity_type="Attachment",
        entity_id="ATT-001",
        action=AuditAction.REMOVED,
    )

    assert audit_log.entity_type == "Attachment"
    assert audit_log.entity_id == "ATT-001"
    assert audit_log.action == AuditAction.REMOVED


def test_audit_log_generates_audit_id():
    audit_log = AuditLog(
        entity_type="Submission",
        entity_id="SUB-001",
        action=AuditAction.CREATED,
    )

    assert isinstance(audit_log.audit_id, str)
    assert len(audit_log.audit_id) > 0


def test_audit_log_generates_unique_ids():
    first = AuditLog(
        entity_type="Submission",
        entity_id="SUB-001",
        action=AuditAction.CREATED,
    )

    second = AuditLog(
        entity_type="Submission",
        entity_id="SUB-001",
        action=AuditAction.CREATED,
    )

    assert first.audit_id != second.audit_id


def test_audit_log_has_created_at():
    audit_log = AuditLog(
        entity_type="Submission",
        entity_id="SUB-001",
        action=AuditAction.CREATED,
    )

    assert isinstance(audit_log.created_at, datetime)


def test_audit_log_rejects_invalid_entity_type():
    with pytest.raises(TypeError):
        AuditLog(
            entity_type=123,
            entity_id="SUB-001",
            action=AuditAction.CREATED,
        )


def test_audit_log_rejects_empty_entity_type():
    with pytest.raises(ValueError):
        AuditLog(
            entity_type="",
            entity_id="SUB-001",
            action=AuditAction.CREATED,
        )


def test_audit_log_rejects_invalid_entity_id():
    with pytest.raises(TypeError):
        AuditLog(
            entity_type="Submission",
            entity_id=123,
            action=AuditAction.CREATED,
        )


def test_audit_log_rejects_empty_entity_id():
    with pytest.raises(ValueError):
        AuditLog(
            entity_type="Submission",
            entity_id="",
            action=AuditAction.CREATED,
        )


def test_audit_log_rejects_invalid_action():
    with pytest.raises(TypeError):
        AuditLog(
            entity_type="Submission",
            entity_id="SUB-001",
            action="created",
        )


def test_audit_log_is_immutable():
    audit_log = AuditLog(
        entity_type="Attachment",
        entity_id="ATT-001",
        action=AuditAction.REMOVED,
    )

    with pytest.raises(AttributeError):
        audit_log.entity_type = "Submission"

    with pytest.raises(AttributeError):
        audit_log.entity_id = "OTHER"

    with pytest.raises(AttributeError):
        audit_log.action = AuditAction.CREATED

    with pytest.raises(AttributeError):
        audit_log.created_at = datetime.now()

    with pytest.raises(AttributeError):
        audit_log.audit_id = "NEW-ID"