from alex.esg.domain.question import Question
from alex.esg.domain.question_category import (
    QuestionCategory,
)
from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.submission_definition_validator import (
    SubmissionDefinitionValidator,
)
from alex.esg.domain.option import Option
from alex.esg.services.import_issue import (
    ImportIssueSeverity,
)

def _create_definition(
    *,
    technical_id: str = "3737695",
    question_code: str = "E1",
) -> QuestionDefinition:
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id=technical_id,
        question_code=question_code,
    )

    return QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=[
            "HU/EGT/Switzerland"
        ],
        topic="Teszt",
        question_type=QuestionType.TEXT,
    )

def test_validator_accepts_matching_question():
    definition = _create_definition()

    response_data = {
        "questions": [
            {
                "id": "3737695",
                "question_id": "E1",
                "fields": [],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert issues == ()

def test_validator_reports_unknown_technical_id():
    definition = _create_definition()

    response_data = {
        "questions": [
            {
                "id": "UNKNOWN_ID",
                "question_id": "E1",
                "fields": [],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert len(issues) == 1

    issue = issues[0]

    assert (
        issue.code
        == "QUESTION_DEFINITION_NOT_FOUND"
    )
def test_validator_reports_question_code_mismatch_as_warning():
    definition = _create_definition(
        technical_id="04DFCA6B_DETAIL1",
        question_code="G9_detail",
    )

    response_data = {
        "questions": [
            {
                "id": "04DFCA6B_DETAIL1",
                "question_id": "G9_detail1",
                "fields": [],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert len(issues) == 1

    issue = issues[0]

    assert (
        issue.code
        == "QUESTION_CODE_MISMATCH"
    )

    assert (
        issue.severity.value
        == "warning"
    )

def test_validator_checks_all_questions():
    definition1 = _create_definition(
        technical_id="TEST_1",
        question_code="E1",
    )

    definition2 = _create_definition(
        technical_id="TEST_2",
        question_code="E2",
    )

    response_data = {
        "questions": [
            {
                "id": "TEST_1",
                "question_id": "E1",
                "fields": [],
            },
            {
                "id": "TEST_2",
                "question_id": "WRONG_CODE",
                "fields": [],
            },
            {
                "id": "TEST_3",
                "question_id": "E3",
                "fields": [],
            },
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition1,
            definition2,
        ),
    )

    codes = {
        issue.code
        for issue in issues
    }

    assert (
        "QUESTION_CODE_MISMATCH"
        in codes
    )

    assert (
        "QUESTION_DEFINITION_NOT_FOUND"
        in codes
    )

def _create_option_definition():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="TEST_RADIO",
        question_code="E1",
    )

    option1 = Option(
        option_id="TEST_RADIO_1",
        label="Igen",
    )

    option2 = Option(
        option_id="TEST_RADIO_2",
        label="Nem",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt kérdés",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.RADIO,
        options=[
            option1,
            option2,
        ],
    )

    return definition

def test_validator_accepts_known_option_id():
    definition = _create_option_definition()

    response_data = {
        "questions": [
            {
                "id": "TEST_RADIO",
                "question_id": "E1",
                "fields": [
                    {
                        "type": "single",
                        "values": [
                            {
                                "optionId": (
                                    "TEST_RADIO_1"
                                ),
                                "selected": True,
                            },
                            {
                                "optionId": (
                                    "TEST_RADIO_2"
                                ),
                                "selected": False,
                            },
                        ],
                    }
                ],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert issues == ()

def test_validator_reports_unknown_option_id():
    definition = _create_option_definition()

    response_data = {
        "questions": [
            {
                "id": "TEST_RADIO",
                "question_id": "E1",
                "fields": [
                    {
                        "type": "single",
                        "values": [
                            {
                                "optionId": (
                                    "TEST_RADIO_999"
                                ),
                                "selected": True,
                            }
                        ],
                    }
                ],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert len(issues) == 1

    assert (
        issues[0].code
        == "UNKNOWN_OPTION_ID"
    )

    assert (
        issues[0].severity
        is ImportIssueSeverity.ERROR
    )

def test_validator_allows_value_without_option_id():
    definition = _create_definition(
        technical_id="NUMBER_TEST",
        question_code="E10",
    )

    response_data = {
        "questions": [
            {
                "id": "NUMBER_TEST",
                "question_id": "E10",
                "fields": [
                    {
                        "type": "number",
                        "values": [
                            {
                                "value": 42
                            }
                        ],
                    }
                ],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert issues == ()

def test_validator_accepts_table_cell_option_ids():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="04E40FB9",
        question_code="E17a",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt táblázat",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.TABLE,
        allowed_value_ids=[
            "04E40FB9_1",
            "04E40FB9_2",
            "04E40FB9_3",
        ],
    )

    response_data = {
        "questions": [
            {
                "id": "04E40FB9",
                "question_id": "E17a",
                "fields": [
                    {
                        "type": "text",
                        "values": [
                            {
                                "optionId": (
                                    "04E40FB9_1"
                                ),
                                "value": "Teszt",
                            }
                        ],
                    },
                    {
                        "type": "number",
                        "values": [
                            {
                                "optionId": (
                                    "04E40FB9_2"
                                ),
                                "value": 12.5,
                            }
                        ],
                    },
                ],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert issues == ()

def test_validator_rejects_unknown_table_cell_id():
    questionnaire = Questionnaire(
        questionnaire_code="SZTFH-ESG",
        spec_version="2.1",
        locale="HU",
    )

    question = Question(
        question_id="04E40FB9",
        question_code="E17a",
    )

    definition = QuestionDefinition(
        question=question,
        questionnaire=questionnaire,
        title="Teszt táblázat",
        category=QuestionCategory.E,
        subject="Environmental",
        organization="SZTFH",
        organization_sizes=["Large"],
        geographical_relevance=["HU"],
        topic="Teszt",
        question_type=QuestionType.TABLE,
        allowed_value_ids=[
            "04E40FB9_1",
            "04E40FB9_2",
        ],
    )

    response_data = {
        "questions": [
            {
                "id": "04E40FB9",
                "question_id": "E17a",
                "fields": [
                    {
                        "type": "text",
                        "values": [
                            {
                                "optionId": (
                                    "04E40FB9_999"
                                ),
                                "value": "Teszt",
                            }
                        ],
                    }
                ],
            }
        ]
    }

    validator = SubmissionDefinitionValidator()

    issues = validator.validate_questions(
        response_data,
        question_definitions=(
            definition,
        ),
    )

    assert any(
        issue.code
        == "UNKNOWN_OPTION_ID"
        for issue in issues
    )