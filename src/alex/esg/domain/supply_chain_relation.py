from uuid import uuid4
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from datetime import datetime, timezone


class SupplyChainRelation:
    def __init__(
        self,
        requester: Company,
        supplier: Supplier,
    ):
        if not isinstance(requester, Company):
            raise TypeError("requester must be a Company")

        if not isinstance(supplier, Supplier):
            raise TypeError("supplier must be a Supplier")

        self.requester = requester
        self.supplier = supplier
        self.relation_id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)



