from dataclasses import dataclass

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.questionnaire import (
    Questionnaire,
)


@dataclass(frozen=True)
class QuestionDefinitionRegistrationResult:
    definitions: tuple[
        QuestionDefinition,
        ...
    ]

    added: tuple[
        QuestionDefinition,
        ...
    ]

    reused: tuple[
        QuestionDefinition,
        ...
    ]

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def reused_count(self) -> int:
        return len(self.reused)


class QuestionDefinitionService:
    def __init__(self) -> None:
        self._definitions: list[
            QuestionDefinition] = []

    def add_definition(
        self,
        definition: QuestionDefinition,
    ) -> QuestionDefinition:
        self._validate_definition(definition)

        existing = self.get_by_question_id(
            questionnaire=(definition.questionnaire),
            question_id=(definition.question.question_id),
        )

        if existing is not None:
            raise ValueError(
                "question definition already exists "
                "for this questionnaire"
            )

        self._definitions.append(definition)

        return definition

    def add_definitions(
        self,
        definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> tuple[
        QuestionDefinition,
        ...
    ]:
        self._validate_definitions_tuple(definitions)

        registered = []

        for definition in definitions:
            registered.append(self.add_definition(definition))

        return tuple(registered)

    def register_definitions(
        self,
        definitions: tuple[
            QuestionDefinition,
            ...
        ],
    ) -> QuestionDefinitionRegistrationResult:
        self._validate_definitions_tuple(definitions)

        resolved: list[QuestionDefinition] = []

        added: list[QuestionDefinition] = []

        reused: list[QuestionDefinition] = []

        for definition in definitions:
            existing = self.get_by_question_id(
                questionnaire=(definition.questionnaire),
                question_id=(definition.question.question_id),
            )

            if existing is None:
                self._definitions.append(definition)

                resolved.append(definition)

                added.append(definition)

                continue

            self._validate_compatible_definition(
                existing=existing,
                incoming=definition,
            )

            resolved.append(existing)

            reused.append(existing)

        return QuestionDefinitionRegistrationResult(
            definitions=tuple(resolved),
            added=tuple(added),
            reused=tuple(reused),
        )

    def list_definitions(
        self,
    ) -> tuple[
        QuestionDefinition,
        ...
    ]:
        return tuple(
            self._definitions
        )

    def list_for_questionnaire(
        self,
        questionnaire: Questionnaire,
    ) -> tuple[
        QuestionDefinition,
        ...
    ]:
        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError(
                "questionnaire must be a "
                "Questionnaire"
            )

        return tuple(
            definition
            for definition in self._definitions
            if self._same_questionnaire(
                definition.questionnaire,
                questionnaire,
            )
        )

    def get_by_question_id(
        self,
        *,
        questionnaire: Questionnaire,
        question_id: str,
    ) -> QuestionDefinition | None:
        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError(
                "questionnaire must be a "
                "Questionnaire"
            )

        if not isinstance(
            question_id,
            str,
        ):
            raise TypeError("question_id must be a string")

        question_id = (question_id.strip())

        if not question_id:
            raise ValueError("question_id cannot be empty")

        for definition in (self._definitions):
            if (
                self._same_questionnaire(definition.questionnaire,
                    questionnaire,
                )
                and (definition.question.question_id == question_id)):
                return definition

        return None

    @staticmethod
    def _validate_definition(
        definition,
    ) -> None:
        if not isinstance(
            definition,
            QuestionDefinition,
        ):
            raise TypeError(
                "definition must be a "
                "QuestionDefinition"
            )

    @classmethod
    def _validate_definitions_tuple(
        cls,
        definitions,
    ) -> None:
        if not isinstance(
            definitions,
            tuple,
        ):
            raise TypeError("definitions must be a tuple")

        for definition in definitions:
            cls._validate_definition(definition)

    @staticmethod
    def _validate_compatible_definition(
        *,
        existing: QuestionDefinition,
        incoming: QuestionDefinition,
    ) -> None:
        existing_code = (existing.question.question_code)

        incoming_code = (incoming.question.question_code)

        if existing_code != incoming_code:
            raise ValueError(
                "conflicting question definition "
                f"for technical id "
                f"{incoming.question.question_id}: "
                f"existing question_code="
                f"{existing_code}, "
                f"incoming question_code="
                f"{incoming_code}"
            )

    @staticmethod
    def _same_questionnaire(
        first: Questionnaire,
        second: Questionnaire,
    ) -> bool:
        return (
            first.questionnaire_code == second.questionnaire_code
            and first.spec_version == second.spec_version
            and first.locale.lower() == second.locale.lower()
        )