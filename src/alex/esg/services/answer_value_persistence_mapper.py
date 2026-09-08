from dataclasses import dataclass
from decimal import Decimal
from alex.esg.services.decimal_value_converter import DecimalValueConverter

@dataclass(frozen=True)
class AnswerValuePersistenceData:
    field_type: str
    option_id: str | None
    selected: bool | None
    number_value: Decimal | None
    text_value: str | None

class AnswerValuePersistenceMapper:
    SUPPORTED_FIELD_TYPES = {
        "single",
        "multi",
        "text",
        "number",
    }

    @staticmethod
    def _optional_text(
        value,
    ) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None
        return text

    @classmethod
    def _map_option_id(
        cls,
        raw_option_id,
        questionnaire_option_ids: set[str],
    ) -> str | None:
        option_id = cls._optional_text(raw_option_id)

        if option_id is None:
            return None

        if option_id not in questionnaire_option_ids:
            return None
        return option_id

    @classmethod
    def map_value(
        cls,
        field_type: str,
        raw_value: dict,
        questionnaire_option_ids: set[str],
    ) -> AnswerValuePersistenceData:
        if not isinstance(
            raw_value,
            dict,
        ):
            raise TypeError("raw_value must be a dict")

        normalized_field_type = (cls._optional_text(field_type))
        if normalized_field_type is None:
            raise ValueError("field_type cannot be empty")

        if (
            normalized_field_type not in cls.SUPPORTED_FIELD_TYPES
        ):
            raise ValueError(
                "unsupported field_type: "
                f"{normalized_field_type}"
            )

        option_id = cls._map_option_id(raw_value.get("optionId"),questionnaire_option_ids,)
        if normalized_field_type in {
            "single",
            "multi",
        }:
            raw_option_id = cls._optional_text(raw_value.get("optionId"))

            if raw_option_id is None:
                raise ValueError(
                    "single/multi value must "
                    "contain optionId"
                )

            if (
                    raw_option_id not in questionnaire_option_ids
            ):
                raise ValueError(
                    "option_id is not valid for "
                    "questionnaire question: "
                    f"{raw_option_id}"
                )
            option_id = raw_option_id
            selected = raw_value.get("selected")
            if not isinstance(
                selected,
                bool,
            ):
                raise ValueError(
                    "single/multi value must "
                    "contain boolean selected"
                )
            return AnswerValuePersistenceData(
                field_type=normalized_field_type,
                option_id=option_id,
                selected=selected,
                number_value=None,
                text_value=None,
            )

        if normalized_field_type == "text":
            text_value = raw_value.get("value")
            if text_value is not None:
                text_value = str(text_value)
            return AnswerValuePersistenceData(
                field_type="text",
                option_id=option_id,
                selected=None,
                number_value=None,
                text_value=text_value,
            )

        number_value = (DecimalValueConverter.to_decimal_18_4(raw_value.get("value")))
        return AnswerValuePersistenceData(
            field_type="number",
            option_id=option_id,
            selected=None,
            number_value=number_value,
            text_value=None,
        )

    @classmethod
    def map_fields(
        cls,
        fields: list[dict],
        questionnaire_option_ids: set[str],
    ) -> list[AnswerValuePersistenceData]:
        if not isinstance(
            fields,
            list,
        ):
            raise TypeError("fields must be a list")
        result = []

        for field in fields:
            if not isinstance(
                field,
                dict,
            ):
                raise TypeError("field must be a dict")

            field_type = field.get("type")
            values = field.get("values") or []

            for raw_value in values:
                result.append(cls.map_value(
                        field_type=field_type,
                        raw_value=raw_value,
                        questionnaire_option_ids=(questionnaire_option_ids),
                    )
                )
        return result