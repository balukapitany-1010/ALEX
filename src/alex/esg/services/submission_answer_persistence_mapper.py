from dataclasses import dataclass
from alex.esg.services.answer_value_persistence_mapper import (
    AnswerValuePersistenceData,
    AnswerValuePersistenceMapper,
)


@dataclass(frozen=True)
class SubmissionAnswerPersistenceData:
    question_id: str
    values: tuple[
        AnswerValuePersistenceData,
        ...
    ]


class SubmissionAnswerPersistenceMapper:
    @staticmethod
    def _required_text(
        value,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(f"{field_name} is required")
        text = str(value).strip()

        if not text:
            raise ValueError(f"{field_name} cannot be empty")
        return text

    @classmethod
    def map_question(
        cls,
        question_payload: dict,
        questionnaire_question_ids: set[str],
        option_ids_by_question: dict[
            str,
            set[str],
        ],
    ) -> (SubmissionAnswerPersistenceData | None):
        if not isinstance(
            question_payload,
            dict,
        ):
            raise TypeError("question_payload must be a dict")

        technical_question_id = (cls._required_text(question_payload.get("id"),
                "question id",
            )
        )
        if (
            technical_question_id not in questionnaire_question_ids
        ):
            return None

        fields = (question_payload.get("fields") or [])

        if not isinstance(
            fields,
            list,
        ):
            raise TypeError("question fields must be a list")

        allowed_option_ids = (option_ids_by_question.get(
                technical_question_id,
                set(),
            )
        )

        values = (AnswerValuePersistenceMapper.map_fields(
                fields=fields,
                questionnaire_option_ids=(allowed_option_ids),
            )
        )

        return SubmissionAnswerPersistenceData(
            question_id=(technical_question_id),
            values=tuple(values),
        )