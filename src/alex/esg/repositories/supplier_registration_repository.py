from abc import ABC, abstractmethod
from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation

class SupplierRegistrationRepository(ABC):
    @abstractmethod
    def register(
        self,
        *,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation:
        pass