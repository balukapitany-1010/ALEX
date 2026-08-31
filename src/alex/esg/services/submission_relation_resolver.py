from alex.esg.domain.supply_chain_relation import (
    SupplyChainRelation,
)
from alex.esg.services.submission_party_resolver import (
    ResolvedSubmissionParties,
)
from alex.esg.services.supply_chain_relation_service import (
    SupplyChainRelationService,
)


class SubmissionRelationResolver:
    def __init__(
        self,
        relation_service: SupplyChainRelationService,
    ) -> None:
        if not isinstance(
            relation_service,
            SupplyChainRelationService,
        ):
            raise TypeError(
                "relation_service must be a "
                "SupplyChainRelationService"
            )

        self._relation_service = relation_service

    def resolve(
        self,
        parties: ResolvedSubmissionParties,
    ) -> SupplyChainRelation:
        if not isinstance(
            parties,
            ResolvedSubmissionParties,
        ):
            raise TypeError(
                "parties must be "
                "ResolvedSubmissionParties"
            )

        existing = self._find_existing_relation(
            parties
        )

        if existing is not None:
            return existing

        return self._relation_service.create_relation(
            requester=parties.requester,
            supplier=parties.supplier,
        )

    def _find_existing_relation(
            self,
            parties: ResolvedSubmissionParties,
    ) -> SupplyChainRelation | None:
        relations = (
            self._relation_service.list_relations_for_requester(
                parties.requester
            )
        )

        for relation in relations:
            if (
                    relation.supplier.company_key
                    == parties.supplier.company_key
            ):
                return relation

        return None