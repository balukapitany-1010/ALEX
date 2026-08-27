from alex.esg.domain.questionnaire import Questionnaire


class QuestionnaireService:
    def __init__(self) -> None:
        self._questionnaires: list[Questionnaire] = []

    def create_questionnaire(
        self,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ) -> Questionnaire:
        questionnaire = Questionnaire(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version,
            locale=locale,
        )

        self._questionnaires.append(questionnaire)

        return questionnaire

    def list_questionnaires(
        self,
    ) -> tuple[Questionnaire, ...]:
        return tuple(self._questionnaires)