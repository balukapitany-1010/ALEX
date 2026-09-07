from typing import Any
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory

class MssqlQuestionnaireDefinitionWriter:
    def __init__(
        self,
        connection_factory: SqlServerConnectionFactory,
    ) -> None:
        if not isinstance(
            connection_factory,
            SqlServerConnectionFactory,
        ):
            raise TypeError(
                "connection_factory must be a "
                "SqlServerConnectionFactory"
            )
        self._connection_factory = (connection_factory)

    def write(
        self,
        *,
        data: dict[str, Any],
        questionnaire_code: str,
    ) -> None:
        if not isinstance(
            data,
            dict,
        ):
            raise TypeError("data must be a dictionary")
        if not isinstance(
            questionnaire_code,
            str,
        ):
            raise TypeError("questionnaire_code must be a string")
        questionnaire_code = (questionnaire_code.strip())
        if not questionnaire_code:
            raise ValueError("questionnaire_code cannot be empty")

        spec_version = self._required_string(
            data,
            "spec_version",
        )
        locale = self._required_string(
            data,
            "locale",
        )
        questions = self._extract_questions(data)
        connection = (self._connection_factory.connect())

        try:
            cursor = connection.cursor()

            self._ensure_questionnaire(
                cursor=cursor,
                questionnaire_code=(questionnaire_code),
                spec_version=spec_version,
                locale=locale,
            )

            for sort_order, question in enumerate(
                questions,
                start=1,
            ):
                self._ensure_question(
                    cursor=cursor,
                    question=question,
                )

                self._ensure_questionnaire_question(
                    cursor=cursor,
                    questionnaire_code=(
                        questionnaire_code
                    ),
                    spec_version=spec_version,
                    question_id=(
                        question["question_id"]
                    ),
                    sort_order=sort_order,
                    status=question["status"],
                )

                for (
                    option_sort_order,
                    option,
                ) in enumerate(
                    question["options"],
                    start=1,
                ):
                    self._ensure_question_option(
                        cursor=cursor,
                        option=option,
                    )

                    if (
                        question["type"]
                        not in {
                            "number",
                            "table",
                        }
                    ):
                        self._ensure_questionnaire_option(
                            cursor=cursor,
                            questionnaire_code=(questionnaire_code),
                            spec_version=(spec_version),
                            question_id=(question["question_id"]),
                            option_id=(option["option_id"]),
                            sort_order=(option_sort_order),
                            status=(option["status"]),
                        )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def _ensure_questionnaire(
        self,
        *,
        cursor,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ) -> None:
        cursor.execute(
            """
            SELECT
                locale
            FROM dbo.QUESTIONNAIRE
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
            """,
            questionnaire_code,
            spec_version,
        )
        row = cursor.fetchone()
        if row is not None:
            existing_locale = str(row[0]).strip()
            if (
                existing_locale.lower() != locale.lower()
            ):
                raise ValueError(
                    "questionnaire locale conflict: "
                    f"database={existing_locale}, "
                    f"incoming={locale}"
                )

            return

        cursor.execute(
            """
            INSERT INTO dbo.QUESTIONNAIRE (
                questionnaire_code,
                spec_version,
                locale,
                created_at
            )
            VALUES (
                ?,
                ?,
                ?,
                SYSUTCDATETIME()
            )
            """,
            questionnaire_code,
            spec_version,
            locale,
        )

    def _ensure_question(
        self,
        *,
        cursor,
        question: dict,
    ) -> None:
        question_id = (question["question_id"])
        cursor.execute(
            """
            SELECT
                question_code,
                category,
                type
            FROM dbo.QUESTION
            WHERE question_id = ?
            """,
            question_id,
        )

        row = cursor.fetchone()
        if row is not None:
            existing_code = self._optional_string(row[0])
            existing_category = (self._optional_string(row[1]))
            existing_type = (self._canonical_question_type(row[2]))
            if (
                existing_code != question["question_code"]
            ):
                raise ValueError("question_code conflict " f"for {question_id}")

            if (
                existing_category != question["category"]
            ):
                raise ValueError("question category conflict " f"for {question_id}")
            if (
                existing_type != question["type"]
            ):
                raise ValueError("question type conflict " f"for {question_id}")
            return
        cursor.execute(
            """
            INSERT INTO dbo.QUESTION (
                question_id,
                requirement,
                topic,
                subtopic,
                title,
                category,
                type,
                question_code,
                visible_if,
                status
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            question_id,
            question["requirement"],
            question["topic"],
            question["subtopic"],
            question["title"],
            question["category"],
            question["db_type"],
            question["question_code"],
            question["visible_if"],
            question["status"],
        )

    def _ensure_questionnaire_question(
        self,
        *,
        cursor,
        questionnaire_code: str,
        spec_version: str,
        question_id: str,
        sort_order: int,
        status: str,
    ) -> None:
        cursor.execute(
            """
            SELECT
                questionnaire_question_id
            FROM dbo.QUESTIONNAIRE_QUESTION
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
                AND question_id = ?
            """,
            questionnaire_code,
            spec_version,
            question_id,
        )
        if cursor.fetchone() is not None:
            return
        cursor.execute(
            """
            INSERT INTO dbo.QUESTIONNAIRE_QUESTION (
                questionnaire_code,
                spec_version,
                question_id,
                sort_order,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            questionnaire_code,
            spec_version,
            question_id,
            sort_order,
            status,
        )

    def _ensure_question_option(
        self,
        *,
        cursor,
        option: dict,
    ) -> None:
        cursor.execute(
            """
            SELECT
                question_id
            FROM dbo.QUESTION_OPTION
            WHERE option_id = ?
            """,
            option["option_id"],
        )
        row = cursor.fetchone()
        if row is not None:
            existing_question_id = str(row[0]).strip()
            if (
                existing_question_id != option["question_id"]
            ):
                raise ValueError(
                    "option belongs to another "
                    "question: "
                    f"{option['option_id']}"
                )
            return
        cursor.execute(
            """
            INSERT INTO dbo.QUESTION_OPTION (
                option_id,
                question_id,
                text,
                status,
                step_value,
                max_value,
                min_value,
                unit,
                input_type
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            option["option_id"],
            option["question_id"],
            option["text"],
            option["status"],
            option["step_value"],
            option["max_value"],
            option["min_value"],
            option["unit"],
            option["input_type"],
        )

    def _ensure_questionnaire_option(
        self,
        *,
        cursor,
        questionnaire_code: str,
        spec_version: str,
        question_id: str,
        option_id: str,
        sort_order: int,
        status: str,
    ) -> None:
        cursor.execute(
            """
            SELECT
                questionnaire_option_id
            FROM dbo.QUESTIONNAIRE_OPTION
            WHERE
                questionnaire_code = ?
                AND spec_version = ?
                AND option_id = ?
            """,
            questionnaire_code,
            spec_version,
            option_id,
        )
        if cursor.fetchone() is not None:
            return
        cursor.execute(
            """
            INSERT INTO dbo.QUESTIONNAIRE_OPTION (
                questionnaire_code,
                spec_version,
                question_id,
                option_id,
                sort_order,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            questionnaire_code,
            spec_version,
            question_id,
            option_id,
            sort_order,
            status,
        )

    def _extract_questions(
        self,
        data: dict[str, Any],
    ) -> list[dict]:
        pages = data.get("pages")
        if not isinstance(
            pages,
            list,
        ):
            raise ValueError("pages must be a list")
        result = []
        current_topic: str | None = None
        for page in pages:
            elements = page.get("elements", [],)
            if not isinstance(
                elements,
                list,
            ):
                raise ValueError("page elements must be a list")
            for element in elements:
                explicit_topic = (self._optional_string(element.get("topic")))

                if explicit_topic is not None:
                    current_topic = (explicit_topic)
                question = (
                    self._extract_question(
                        element=element,
                        fallback_topic=(current_topic),
                    )
                )
                result.append(question)
        return result

    def _extract_question(
        self,
        *,
        element: dict,
        fallback_topic: str | None,
    ) -> dict:
        question_id = (self._required_string(element, "ID",))
        question_code = (self._required_string(element, "name",))
        db_type = (self._required_string(element, "type",).lower())
        canonical_type = (self._canonical_question_type(db_type))
        topic = (self._optional_string(element.get("topic")) or fallback_topic or "-")
        title = (self._optional_string(element.get("title")) or question_code)
        status = (self._optional_string(element.get("status")) or "active")
        options = (
            self._extract_options(
                element=element,
                question_id=question_id,
                question_type=(canonical_type),
                status=status,
            )
        )

        return {
            "question_id": question_id,
            "question_code": (question_code),
            "requirement": (self._optional_string(element.get("requirement"))),
            "topic": topic,
            "subtopic": (self._optional_string(element.get("subtopic"))),
            "title": title,
            "category": (self._required_string(element,"category",).upper()),
            "type": canonical_type,
            "db_type": db_type,
            "visible_if": (self._optional_string(element.get("visibleIf"))),
            "status": status,
            "options": options,
        }

    def _extract_options(
        self,
        *,
        element: dict,
        question_id: str,
        question_type: str,
        status: str,
    ) -> list[dict]:
        result: list[dict] = []
        seen: set[str] = set()

        def add(
            *,
            option_id,
            text=None,
            option_status="active",
            step_value=None,
            max_value=None,
            min_value=None,
            unit=None,
            input_type=None,
        ) -> None:
            if option_id is None:
                return
            option_id = str(option_id).strip()
            if not option_id:
                return
            if option_id in seen:
                return
            seen.add(option_id)
            result.append(
                {
                    "option_id": (option_id),
                    "question_id": (question_id),
                    "text": (self._optional_string(text)),
                    "status": (self._optional_string(option_status) or "active"),
                    "step_value": (step_value),
                    "max_value": (max_value),
                    "min_value": (min_value),
                    "unit": (self._optional_string(unit)),
                    "input_type": (self._optional_string(input_type)),
                }
            )

        choices = (element.get("choices") or [])

        for choice in choices:
            if not isinstance(
                choice,
                dict,
            ):
                continue

            add(
                option_id=(choice.get("value")),
                text=(choice.get("text")),
                option_status=(choice.get("status") or "active"),
                step_value=(choice.get("step")),
                max_value=(choice.get("max")),
                min_value=(choice.get("min")),
                unit=(choice.get("unit")),
                input_type=(choice.get("inputType")),
            )

        columns = (element.get("columns") or [])
        for column in columns:
            if not isinstance(
                column,
                dict,
            ):
                continue

            for cell in (column.get("cells") or []
            ):
                if not isinstance(
                    cell,
                    dict,
                ):
                    continue

                add(
                    option_id=(cell.get("value")),
                    text=(cell.get("text")),
                    option_status=(cell.get("status") or "active"),
                    step_value=(cell.get("step")),
                    max_value=(cell.get("max")),
                    min_value=(cell.get("min")),
                    unit=(cell.get("unit")),
                    input_type=(cell.get("inputType")),
                )

        if (
            question_type == "number"
        ):
            add(
                option_id=question_id,
                text=None,
                option_status=status,
                step_value=(element.get("step")),
                max_value=(element.get("max")),
                min_value=(element.get("min")),
                unit=(element.get("unit")),
                input_type="number",
            )

        return result

    @staticmethod
    def _canonical_question_type(
        value,
    ) -> str:
        normalized = str(value).strip().lower()
        mapping = {
            "radio": "radio",
            "radiogroup": "radio",
            "checkbox": "checkbox",
            "dropdown": "dropdown",
            "text": "text",
            "comment": "comment",
            "number": "number",
            "mixed": "mixed",
            "table": "table",
        }

        result = mapping.get(normalized)
        if result is None:
            raise ValueError("unsupported question type: " f"{value}")
        return result

    @staticmethod
    def _required_string(
        data: dict,
        key: str,
    ) -> str:
        value = data.get(key)
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(f"{key} must be a string")
        value = value.strip()
        if not value:
            raise ValueError(f"{key} cannot be empty")
        return value

    @staticmethod
    def _optional_string(
        value,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "optional value must be "
                "a string or None"
            )

        value = value.strip()
        return value or None