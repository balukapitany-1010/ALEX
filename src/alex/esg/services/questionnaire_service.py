from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.repositories.in_memory_questionnaire_repository import InMemoryQuestionnaireRepository
from alex.esg.repositories.questionnaire_repository import QuestionnaireRepository

class QuestionnaireService:
    def __init__(
        self,
        repository: QuestionnaireRepository | None = None,
    ) -> None:
        if repository is None:
            repository = (InMemoryQuestionnaireRepository())
        if not isinstance(
            repository,
            QuestionnaireRepository,
        ):
            raise TypeError(
                "repository must be a "
                "QuestionnaireRepository"
            )
        self._repository = repository

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
        return self._repository.add(questionnaire)

    def list_questionnaires(
        self,
    ) -> tuple[Questionnaire, ...]:
        return self._repository.list_all()

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
            raise TypeError("questionnaire_code must be a string")

        if not isinstance(
            spec_version,
            str,
        ):
            raise TypeError("spec_version must be a string")

        if not isinstance(
            locale,
            str,
        ):
            raise TypeError("locale must be a string")
        questionnaire_code = (questionnaire_code.strip())
        spec_version = (spec_version.strip())
        locale = (locale.strip())
        if not questionnaire_code:
            raise ValueError("questionnaire_code cannot be empty")
        if not spec_version:
            raise ValueError("spec_version cannot be empty")
        if not locale:
            raise ValueError("locale cannot be empty")
        return self._repository.get_by_identity(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version,
            locale=locale,
        )

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