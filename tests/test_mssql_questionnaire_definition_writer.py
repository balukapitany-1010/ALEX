from unittest.mock import MagicMock
from alex.esg.repositories.mssql_questionnaire_definition_writer import MssqlQuestionnaireDefinitionWriter
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

def test_writer_rolls_back_when_write_fails():
    factory = MagicMock(spec=SqlServerConnectionFactory)
    connection = MagicMock()
    cursor = MagicMock()
    factory.connect.return_value = (connection)
    connection.cursor.return_value = (cursor)
    cursor.fetchone.side_effect = (RuntimeError("database failure"))
    writer = (MssqlQuestionnaireDefinitionWriter(factory))

    data = {
        "spec_version": "2.1",
        "locale": "HU",
        "pages": [],
    }

    try:
        writer.write(
            data=data,
            questionnaire_code="SZTFH",
        )

    except RuntimeError:
        pass

    else:
        raise AssertionError("RuntimeError was expected")
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    connection.close.assert_called_once()

def test_writer_inserts_number_question_option_with_metadata():
    factory = MagicMock(spec=SqlServerConnectionFactory)
    connection = MagicMock()
    cursor = MagicMock()
    factory.connect.return_value = (connection)
    connection.cursor.return_value = (cursor)
    cursor.fetchone.return_value = None
    writer = (MssqlQuestionnaireDefinitionWriter(factory))
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E20b_detail",
                        "title": (
                            "Összes pontforráshoz "
                            "viszonyított százalékos "
                            "érték megadása szükséges."
                        ),
                        "type": "number",
                        "min": 0,
                        "max": 100,
                        "step": 0.01,
                        "unit": "%",
                        "category": "E",
                        "ID": "0072BD9B_DETAIL",
                        "topic": "Éghajlatváltozás",
                        "status": "active",
                    }
                ]
            }
        ],
    }

    writer.write(
        data=data,
        questionnaire_code="SZTFH",
    )

    question_option_calls = []

    for call in cursor.execute.call_args_list:
        sql = call.args[0]

        if (
            "INSERT INTO dbo.QUESTION_OPTION"
            in sql
        ):
            question_option_calls.append(call)

    assert len(question_option_calls) == 1
    call = question_option_calls[0]
    assert call.args[1:] == (
        "0072BD9B_DETAIL",
        "0072BD9B_DETAIL",
        None,
        "active",
        0.01,
        100,
        0,
        "%",
        "number",
    )
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()

def test_writer_does_not_link_number_option_to_questionnaire():
    factory = MagicMock(spec=SqlServerConnectionFactory)
    connection = MagicMock()
    cursor = MagicMock()
    factory.connect.return_value = (connection)
    connection.cursor.return_value = (cursor)
    cursor.fetchone.return_value = None
    writer = (MssqlQuestionnaireDefinitionWriter(factory))
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E20b_detail",
                        "title": "Teszt number kérdés",
                        "type": "number",
                        "min": 0,
                        "max": 100,
                        "step": 0.01,
                        "unit": "%",
                        "category": "E",
                        "ID": "0072BD9B_DETAIL",
                        "topic": "Éghajlatváltozás",
                        "status": "active",
                    }
                ]
            }
        ],
    }
    writer.write(
        data=data,
        questionnaire_code="SZTFH",
    )
    executed_sql = "\n".join(str(call.args[0]) for call in cursor.execute.call_args_list)
    assert ("INSERT INTO dbo.QUESTION_OPTION" in executed_sql)
    assert ("INSERT INTO dbo.QUESTIONNAIRE_OPTION" not in executed_sql)

def test_writer_is_idempotent_when_everything_already_exists():
    factory = MagicMock(spec=SqlServerConnectionFactory)
    connection = MagicMock()
    cursor = MagicMock()
    factory.connect.return_value = (connection)
    connection.cursor.return_value = (cursor)
    cursor.fetchone.side_effect = [
        ("HU",),
        (
            "E1",
            "E",
            "radiogroup",
        ),
        (1,),
        ("TEST_QUESTION",),
        (1,),
    ]
    writer = (MssqlQuestionnaireDefinitionWriter(factory))
    data = {
        "spec_version": "2.0",
        "locale": "HU",
        "pages": [
            {
                "elements": [
                    {
                        "name": "E1",
                        "title": "Teszt kérdés",
                        "type": "radiogroup",
                        "category": "E",
                        "ID": "TEST_QUESTION",
                        "topic": "Teszt téma",
                        "status": "active",
                        "choices": [
                            {
                                "value": "TEST_OPTION_1",
                                "text": "Igen",
                                "status": "active",
                            }
                        ],
                    }
                ]
            }
        ],
    }

    writer.write(
        data=data,
        questionnaire_code="SZTFH",
    )

    executed_sql = "\n".join(str(call.args[0]) for call in cursor.execute.call_args_list)
    assert ("INSERT INTO dbo.QUESTIONNAIRE (" not in executed_sql)
    assert ("INSERT INTO dbo.QUESTION (" not in executed_sql)
    assert ("INSERT INTO dbo.QUESTIONNAIRE_QUESTION" not in executed_sql)
    assert ("INSERT INTO dbo.QUESTION_OPTION" not in executed_sql)
    assert ("INSERT INTO dbo.QUESTIONNAIRE_OPTION" not in executed_sql)
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()