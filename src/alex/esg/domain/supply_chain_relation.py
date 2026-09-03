from datetime import UTC, datetime
from uuid import uuid4
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier


class SupplyChainRelation:
    def __init__(
        self,
        requester: Company,
        supplier: Supplier,
    ) -> None:
        if not isinstance(
            requester,
            Company,
        ):
            raise TypeError("requester must be a Company")

        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError("supplier must be a Supplier")
        now = datetime.now(UTC)
        self.requester = requester
        self.supplier = supplier
        self.relation_id = str(uuid4())
        self.relation_status = ("active")
        self.created_at = now
        self.updated_at = now

    @classmethod
    def rehydrate(
        cls,
        *,
        relation_id: int | str,
        requester: Company,
        supplier: Supplier,
        relation_status: str | None,
        created_at: datetime,
        updated_at: datetime | None,
    ) -> "SupplyChainRelation":
        if not isinstance(
            relation_id,
            (int, str),
        ):
            raise TypeError("relation_id must be an int or string")
        normalized_relation_id = str(relation_id).strip()

        if not normalized_relation_id:
            raise ValueError("relation_id cannot be empty")

        if not isinstance(
            requester,
            Company,
        ):
            raise TypeError("requester must be a Company")
        if not isinstance(
            supplier,
            Supplier,
        ):
            raise TypeError("supplier must be a Supplier")
        if (
            relation_status is not None
            and not isinstance(
                relation_status,
                str,
            )
        ):
            raise TypeError(
                "relation_status must be "
                "a string or None"
            )
        if not isinstance(
            created_at,
            datetime,
        ):
            raise TypeError("created_at must be a datetime")
        if (
            updated_at is not None
            and not isinstance(
                updated_at,
                datetime,
            )
        ):
            raise TypeError(
                "updated_at must be "
                "a datetime or None"
            )

        if created_at.tzinfo is None:
            created_at = (created_at.replace(tzinfo=UTC))
        else:
            created_at = (created_at.astimezone(UTC))
        if updated_at is not None:
            if updated_at.tzinfo is None:
                updated_at = (updated_at.replace(tzinfo=UTC))
            else:
                updated_at = (updated_at.astimezone(UTC))

        relation = cls(
            requester=requester,
            supplier=supplier,
        )
        relation.relation_id = (normalized_relation_id)
        relation.relation_status = (relation_status or "active")
        relation.created_at = (created_at)
        relation.updated_at = (updated_at)
        return relation