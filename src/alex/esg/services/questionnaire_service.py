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

    def get_by_identity(
            self,
            *,
            questionnaire_code: str,
            spec_version: str,
            locale: str,
    ) -> Questionnaire | None:
        if not isinstance(
                questionnaire_code,
                str,
        ):
            raise TypeError(
                "questionnaire_code must be a string"
            )

        if not isinstance(
                spec_version,
                str,
        ):
            raise TypeError(
                "spec_version must be a string"
            )

        if not isinstance(
                locale,
                str,
        ):
            raise TypeError(
                "locale must be a string"
            )

        questionnaire_code = (
            questionnaire_code.strip()
        )

        spec_version = (
            spec_version.strip()
        )

        locale = (
            locale.strip()
        )

        if not questionnaire_code:
            raise ValueError(
                "questionnaire_code cannot be empty"
            )

        if not spec_version:
            raise ValueError(
                "spec_version cannot be empty"
            )

        if not locale:
            raise ValueError(
                "locale cannot be empty"
            )

        for questionnaire in (
                self.list_questionnaires()
        ):
            if (
                    questionnaire.questionnaire_code
                    == questionnaire_code
                    and questionnaire.spec_version
                    == spec_version
                    and questionnaire.locale.lower()
                    == locale.lower()
            ):
                return questionnaire

        return None

    def get_or_create(
            self,
            *,
            questionnaire_code: str,
            spec_version: str,
            locale: str,
    ) -> Questionnaire:
        existing = self.get_by_identity(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version,
            locale=locale,
        )

        if existing is not None:
            return existing

        return self.create_questionnaire(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version,
            locale=locale,
        )