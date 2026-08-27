from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


class SupplyChainRelationService:
    def __init__(self) -> None:
        self._relations: list[SupplyChainRelation] = []

    def create_relation(
        self,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation:
        if self.get_relation(
            requester=requester,
            supplier=supplier,
        ) is not None:
            raise ValueError(
                "relation between requester and supplier already exists"
            )

        relation = SupplyChainRelation(
            requester=requester,
            supplier=supplier,
        )

        self._relations.append(relation)

        return relation

    def list_relations(
        self,
    ) -> tuple[SupplyChainRelation, ...]:
        return tuple(self._relations)

    def get_relation(
        self,
        requester: Company,
        supplier: Supplier,
    ) -> SupplyChainRelation | None:
        for relation in self._relations:
            if (
                relation.requester is requester
                and relation.supplier is supplier
            ):
                return relation

        return None

    def list_relations_for_requester(
        self,
        requester: Company,
    ) -> tuple[SupplyChainRelation, ...]:
        return tuple(
            relation
            for relation in self._relations
            if relation.requester is requester
        )

    def list_relations_for_supplier(
        self,
        supplier: Supplier,
    ) -> tuple[SupplyChainRelation, ...]:
        return tuple(
            relation
            for relation in self._relations
            if relation.supplier is supplier
        )