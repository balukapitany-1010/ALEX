from abc import ABC, abstractmethod

from alex.esg.domain.submission import Submission
from alex.esg.domain.supply_chain_relation import SupplyChainRelation

class SubmissionRepository(ABC):
    @abstractmethod
    def add(
        self,
        submission: Submission,
    ) -> Submission:
        pass

    @abstractmethod
    def list_all(
        self,
    ) -> tuple[Submission, ...]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        submission_id: str,
    ) -> Submission | None:
        pass

    def remove(
            self,
            relation_id: str,
    ) -> SupplyChainRelation:
        relation = self.get_by_id( relation_id)

        if relation is None:
            raise ValueError("relation does not exist")

        self._relations.remove(relation)

        return relation

    @abstractmethod
    def remove(
            self,
            submission_id: str,
    ) -> Submission:
        pass