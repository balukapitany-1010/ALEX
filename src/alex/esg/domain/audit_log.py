from datetime import datetime, timezone
from uuid import uuid4

from alex.esg.domain.audit_action import AuditAction


class AuditLog:
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        action: AuditAction,
    ):
        if not isinstance(entity_type, str):
            raise TypeError("entity_type must be a string")

        if not entity_type.strip():
            raise ValueError("entity_type cannot be empty")

        if not isinstance(entity_id, str):
            raise TypeError("entity_id must be a string")

        if not entity_id.strip():
            raise ValueError("entity_id cannot be empty")

        if not isinstance(action, AuditAction):
            raise TypeError("action must be an AuditAction")

        self._audit_id = str(uuid4())
        self._entity_type = entity_type
        self._entity_id = entity_id
        self._action = action
        self._created_at = datetime.now(timezone.utc)

    @property
    def audit_id(self) -> str:
        return self._audit_id

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def action(self) -> AuditAction:
        return self._action

    @property
    def created_at(self) -> datetime:
        return self._created_at