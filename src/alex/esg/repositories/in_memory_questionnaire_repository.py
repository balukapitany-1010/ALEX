from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.repositories.questionnaire_repository import QuestionnaireRepository

class InMemoryQuestionnaireRepository(
    QuestionnaireRepository
):
    def __init__(self) -> None:
        self._questionnaires: list[
            Questionnaire
        ] = []

    def add(
        self,
        questionnaire: Questionnaire,
    ) -> Questionnaire:
        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError("questionnaire must be a Questionnaire")
        self._questionnaires.append(questionnaire)
        return questionnaire

    def list_all(
        self,
    ) -> tuple[Questionnaire, ...]:
        return tuple(self._questionnaires)

    def get_by_identity(
        self,
        *,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ) -> Questionnaire | None:
        for questionnaire in (self._questionnaires
        ):
            if (
                questionnaire.questionnaire_code == questionnaire_code and questionnaire.spec_version == spec_version and questionnaire.locale.lower() == locale.lower()
            ):
                return questionnaire
        return None