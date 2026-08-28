from typing import Any

from alex.esg.domain.option import Option
from alex.esg.domain.question import Question
from alex.esg.domain.question_category import QuestionCategory
from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.question_type import QuestionType
from alex.esg.domain.questionnaire import Questionnaire


class QuestionnaireDefinitionMapper:
    def map(
        self,
        data: dict[str, Any],
        *,
        questionnaire_code: str,
    ) -> tuple[
        Questionnaire,
        tuple[QuestionDefinition, ...],
    ]:
        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary"
            )

        if not isinstance(questionnaire_code, str):
            raise TypeError(
                "questionnaire_code must be a string"
            )

        questionnaire_code = questionnaire_code.strip()

        if not questionnaire_code:
            raise ValueError(
                "questionnaire_code cannot be empty"
            )

        spec_version = data.get(
            "spec_version"
        )

        locale = data.get(
            "locale"
        )

        pages = data.get(
            "pages"
        )

        if not isinstance(spec_version, str):
            raise ValueError(
                "spec_version is required"
            )

        if not spec_version.strip():
            raise ValueError(
                "spec_version cannot be empty"
            )

        if not isinstance(locale, str):
            raise ValueError(
                "locale is required"
            )

        if not locale.strip():
            raise ValueError(
                "locale cannot be empty"
            )

        if not isinstance(pages, list):
            raise ValueError(
                "pages must be a list"
            )

        questionnaire = Questionnaire(
            questionnaire_code=questionnaire_code,
            spec_version=spec_version.strip(),
            locale=locale.strip(),
        )

        definitions: list[QuestionDefinition] = []

        for page in pages:
            if not isinstance(page, dict):
                raise ValueError(
                    "page must be an object"
                )

            elements = page.get(
                "elements",
                [],
            )

            if not isinstance(elements, list):
                raise ValueError(
                    "page elements must be a list"
                )

            current_topic: str | None = None

            for element in elements:
                if not isinstance(element, dict):
                    raise ValueError(
                        "question element must be an object"
                    )

                explicit_topic = self._optional_string(
                    element.get("topic")
                )

                if explicit_topic is not None:
                    current_topic = explicit_topic

                definition = self._map_element(
                    element=element,
                    questionnaire=questionnaire,
                    fallback_topic=current_topic,
                )

                definitions.append(
                    definition
                )

        return (
            questionnaire,
            tuple(definitions),
        )

    def _map_element(
        self,
        *,
        element: dict[str, Any],
        questionnaire: Questionnaire,
        fallback_topic: str | None = None,
    ) -> QuestionDefinition:
        if not isinstance(element, dict):
            raise ValueError(
                "question element must be an object"
            )

        question_id = self._required_string(
            element,
            "ID",
        )

        question_code = self._required_string(
            element,
            "name",
        )


        title = (
            self._optional_string(
                element.get("title")
            )
            or question_code
        )

        category = self._map_category(
            self._required_string(
                element,
                "category",
            )
        )

        question_type = self._map_question_type(
            self._required_string(
                element,
                "type",
            )
        )

        subject = self._get_subject(
            element
        )


        organization = self._get_organization(
            element
        )

        organization_sizes = element.get(
            "organization_size",
            [],
        )

        geographical_relevance = element.get(
            "GeographicalRelevance",
            [],
        )


        topic = self._optional_string(
            element.get("topic")
        )

        if topic is None:
            if (
                "_detail" not in question_code.lower()
                or fallback_topic is None
            ):
                raise ValueError(
                    "topic must be a string"
                )

            topic = fallback_topic

        subtopic = self._optional_string(
            element.get("subtopic")
        )

        requirement = self._optional_string(
            element.get("requirement")
        )

        question = Question(
            question_id=question_id,
            question_code=question_code,
        )

        #
        # Klasszikus válaszopciók.
        #
        if question_type in {
            QuestionType.RADIO,
            QuestionType.CHECKBOX,
            QuestionType.DROPDOWN,
        }:
            options = self._map_options(
                element.get("choices")
            )


        elif question_type == QuestionType.MIXED:
            options = self._map_mixed_options(
                element.get("choices")
            )


        else:
            options = []

        return QuestionDefinition(
            question=question,
            questionnaire=questionnaire,
            title=title,
            category=category,
            subject=subject,
            organization=organization,
            organization_sizes=organization_sizes,
            geographical_relevance=geographical_relevance,
            topic=topic,
            subtopic=subtopic,
            requirement=requirement,
            question_type=question_type,
            options=options,
        )

    def _map_mixed_options(
        self,
        choices: Any,
    ) -> list[Option]:
        if choices is None:
            return []

        if not isinstance(choices, list):
            raise ValueError(
                "choices must be a list"
            )

        selectable_choices: list[
            dict[str, Any]
        ] = []

        for choice in choices:
            if not isinstance(choice, dict):
                raise ValueError(
                    "choice must be an object"
                )


            if choice.get("inputType") is not None:
                continue

            selectable_choices.append(
                choice
            )

        return self._map_options(
            selectable_choices
        )

    def _map_options(
        self,
        choices: Any,
    ) -> list[Option]:
        if choices is None:
            return []

        if not isinstance(choices, list):
            raise ValueError(
                "choices must be a list"
            )

        options: list[Option] = []

        for choice in choices:
            if not isinstance(choice, dict):
                raise ValueError(
                    "choice must be an object"
                )

            status = choice.get(
                "status"
            )


            if (
                isinstance(status, str)
                and status.strip().lower()
                == "inactive"
            ):
                continue

            option_id = self._required_string(
                choice,
                "value",
            )

            label = choice.get(
                "text"
            )

            if not isinstance(label, str):
                raise ValueError(
                    "option label must be a string: "
                    f"{option_id}"
                )

            label = label.strip()

            if not label:
                raise ValueError(
                    "option label cannot be empty: "
                    f"{option_id}"
                )

            options.append(
                Option(
                    option_id=option_id,
                    label=label,
                )
            )

        return options

    @staticmethod
    def _map_category(
        value: str,
    ) -> QuestionCategory:
        try:
            return QuestionCategory[
                value.upper()
            ]

        except KeyError as error:
            raise ValueError(
                "unsupported question category: "
                f"{value}"
            ) from error

    @staticmethod
    def _map_question_type(
        value: str,
    ) -> QuestionType:
        normalized = (
            value.strip().lower()
        )

        mapping = {
            "radiogroup": QuestionType.RADIO,
            "radio": QuestionType.RADIO,
            "checkbox": QuestionType.CHECKBOX,
            "dropdown": QuestionType.DROPDOWN,
            "text": QuestionType.TEXT,
            "comment": QuestionType.COMMENT,
            "number": QuestionType.NUMBER,
            "mixed": QuestionType.MIXED,
            "table": QuestionType.TABLE,
        }

        question_type = mapping.get(
            normalized
        )

        if question_type is None:
            raise ValueError(
                "unsupported JSON question type: "
                f"{value}"
            )

        return question_type

    @staticmethod
    def _required_string(
        data: dict[str, Any],
        key: str,
    ) -> str:
        value = data.get(
            key
        )

        if not isinstance(value, str):
            raise ValueError(
                f"{key} must be a string"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{key} cannot be empty"
            )

        return value

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(
                "optional value must be "
                "a string or None"
            )

        value = value.strip()

        return value or None

    @staticmethod
    def _get_subject(
        element: dict[str, Any],
    ) -> str:
        subject = element.get(
            "subject"
        )

        if (
            isinstance(subject, str)
            and subject.strip()
        ):
            return subject.strip()

        category = element.get(
            "category",
            "",
        )

        if category == "E":
            return "Environmental"

        if category == "S":
            return "Social"

        if category == "G":
            return "Governance"

        return "ESG"

    @staticmethod
    def _get_organization(
        element: dict[str, Any],
    ) -> str:
        organization = element.get(
            "organization"
        )

        if (
            isinstance(organization, str)
            and organization.strip()
        ):
            return organization.strip()

        return "SZTFH"