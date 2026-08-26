from enum import Enum

class AuditAction(Enum):
    CREATED = "created"
    UPDATED = "updated"
    REMOVED = "removed"
    ARCHIVED = "archived"
    RESTORED = "restored"