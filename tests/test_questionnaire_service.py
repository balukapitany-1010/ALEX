from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.questionnaire_service import QuestionnaireService


def test_questionnaire_service_can_create_questionnaire():
    service = QuestionnaireService()

    questionnaire = service.create_questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    assert isinstance(questionnaire, Questionnaire)
    assert questionnaire.questionnaire_code == "SZTFH-ESG"
    assert questionnaire.spec_version == "2.1"
    assert questionnaire.locale == "hu"


def test_questionnaire_service_lists_questionnaires():
    service = QuestionnaireService()

    questionnaire = service.create_questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    assert service.list_questionnaires() == (
        questionnaire,
    )