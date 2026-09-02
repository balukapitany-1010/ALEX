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

def test_questionnaire_service_get_by_identity():
    service = QuestionnaireService()

    questionnaire = (
        service.create_questionnaire(
            questionnaire_code="SZTFH-ESG",
            spec_version="2.1",
            locale="HU",
        )
    )

    result = service.get_by_identity(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    assert result is questionnaire


def test_questionnaire_service_identity_locale_is_case_insensitive():
    service = QuestionnaireService()

    questionnaire = (
        service.create_questionnaire(
            questionnaire_code="SZTFH-ESG",
            spec_version="2.1",
            locale="hu",
        )
    )

    result = service.get_by_identity(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    assert result is questionnaire


def test_questionnaire_service_get_by_identity_returns_none():
    service = QuestionnaireService()

    result = service.get_by_identity(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    assert result is None


def test_questionnaire_service_get_or_create_creates_questionnaire():
    service = QuestionnaireService()

    result = service.get_or_create(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    assert (
        service.list_questionnaires()
        == (result,)
    )


def test_questionnaire_service_get_or_create_reuses_questionnaire():
    service = QuestionnaireService()

    first = service.get_or_create(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    second = service.get_or_create(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="hu",
    )

    assert second is first

    assert len(
        service.list_questionnaires()
    ) == 1

