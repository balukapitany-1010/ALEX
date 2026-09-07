from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.repositories.mssql_question_definition_repository import MssqlQuestionDefinitionRepository

class QuestionDefinitionReadService:
    def __init__(
        self,
        repository: MssqlQuestionDefinitionRepository,
    ) -> None:
        if not isinstance(
            repository,
            MssqlQuestionDefinitionRepository,
        ):
            raise TypeError(
                "repository must be an "
                "MssqlQuestionDefinitionRepository"
            )

        self._repository = repository

    def list_for_questionnaire(
        self,
        questionnaire: Questionnaire,
    ) -> tuple[QuestionDefinition, ...]:
        return (self._repository.list_for_questionnaire(questionnaire))

    def get_by_question_id(
        self,
        *,
        questionnaire: Questionnaire,
        question_id: str,
    ) -> QuestionDefinition | None:
        return (
            self._repository
            .get_by_question_id(
                questionnaire=questionnaire,
                question_id=question_id,
            )
        )