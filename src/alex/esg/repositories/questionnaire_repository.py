from abc import ABC, abstractmethod
from alex.esg.domain.questionnaire import Questionnaire

class QuestionnaireRepository(ABC):
    @abstractmethod
    def add(
        self,
        questionnaire: Questionnaire,
    ) -> Questionnaire:
        pass

    @abstractmethod
    def list_all(
        self,
    ) -> tuple[Questionnaire, ...]:
        pass

    @abstractmethod
    def get_by_identity(
        self,
        *,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ) -> Questionnaire | None:
        pass