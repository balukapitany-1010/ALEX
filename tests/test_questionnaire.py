import pytest

from alex.esg.domain.questionnaire import Questionnaire


def test_questionnaire_can_be_created():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )

    assert questionnaire.questionnaire_code == "SZTFH"
    assert questionnaire.spec_version == "2.1"
    assert questionnaire.locale == "hu"


def test_questionnaire_rejects_empty_code():
    with pytest.raises(ValueError):
        Questionnaire(
            questionnaire_code="",
            spec_version="2.1",
            locale="hu",
        )


def test_questionnaire_rejects_empty_version():
    with pytest.raises(ValueError):
        Questionnaire(
            questionnaire_code="SZTFH",
            spec_version="",
            locale="hu",
        )


def test_questionnaire_rejects_empty_locale():
    with pytest.raises(ValueError):
        Questionnaire(
            questionnaire_code="SZTFH",
            spec_version="2.1",
            locale="",
        )

def test_questionnaire_key_contains_code_version_and_locale():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    assert questionnaire.questionnaire_key == "SZTFH:2.1:hu"

def test_different_questionnaire_versions_have_different_keys():
    version_20= Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.0",
        locale="hu",
    )
    version_21= Questionnaire(
        questionnaire_code="SZTFH",
        spec_version="2.1",
        locale="hu",
    )
    assert version_20.questionnaire_key != version_21.questionnaire_key