from abc import ABC, abstractmethod

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


class SupplyChainRelationRepository(ABC):
    @abstractmethod
    def add(
        self,
        relation: SupplyChainRelation,
    ) -> SupplyChainRelation:
        pass

    @abstractmethod
    def list_all(
        self,
    ) -> tuple[SupplyChainRelation, ...]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        relation_id: str,
    ) -> SupplyChainRelation | None:
        pass

    @abstractmethod
    def get_by_parties(
        self,
        *,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation | None:
        pass

    @abstractmethod
    def list_for_requester(
        self,
        requester: Company,
    ) -> tuple[SupplyChainRelation, ...]:
        pass

    @abstractmethod
    def list_for_supplier(
        self,
        supplier: Supplier,
    ) -> tuple[SupplyChainRelation, ...]:
        pass

    @abstractmethod
    def remove(
            self,
            relation_id: str,
    ) -> SupplyChainRelation:
        pass