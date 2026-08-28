class AnswerValue:
    _ALLOWED_FIELD_TYPES = {
        "single",
        "multi",
        "text",
        "number",
    }

    def __init__(
        self,
        field_type: str,
        *,
        option_id: str | None = None,
        selected: bool | None = None,
        text_value: str | None = None,
        number_value: int | float | None = None,
    ) -> None:
        if not isinstance(field_type, str):
            raise TypeError("field_type must be a string")

        normalized_field_type = (
            field_type.strip().lower()
        )

        if not normalized_field_type:
            raise ValueError("field_type cannot be empty")

        if (normalized_field_type not in self._ALLOWED_FIELD_TYPES):
            raise ValueError(f"unsupported field_type: "f"{normalized_field_type}"
            )

        if option_id is not None:
            if not isinstance(option_id, str):
                raise TypeError("option_id must be a string or None")

            option_id = option_id.strip()

            if not option_id:
                raise ValueError("option_id cannot be empty")

        if selected is not None:
            if not isinstance(selected, bool):
                raise TypeError("selected must be a bool or None")

        if text_value is not None:
            if not isinstance(text_value, str):
                raise TypeError("text_value must be a string or None")

        if number_value is not None:
            if (
                isinstance(number_value, bool)
                or not isinstance(
                    number_value,
                    (int, float),
                )
            ):
                raise TypeError("number_value must be ""an int, float or None")

        self._validate_value_combination(
            field_type=normalized_field_type,
            selected=selected,
            text_value=text_value,
            number_value=number_value,
        )

        self._field_type = normalized_field_type
        self._option_id = option_id
        self._selected = selected
        self._text_value = text_value
        self._number_value = number_value

    @staticmethod
    def _validate_value_combination(
        *,
        field_type: str,
        selected: bool | None,
        text_value: str | None,
        number_value: int | float | None,
    ) -> None:
        if field_type in {"single", "multi"}:
            if text_value is not None:
                raise ValueError( f"{field_type} field ""cannot have text_value")

            if number_value is not None:
                raise ValueError(f"{field_type} field ""cannot have number_value")

        elif field_type == "text":
            if selected is not None:
                raise ValueError("text field cannot have selected")

            if number_value is not None:
                raise ValueError("text field cannot have ""number_value")

        elif field_type == "number":
            if selected is not None:
                raise ValueError("number field cannot have ""selected")

            if text_value is not None:
                raise ValueError("number field cannot have ""text_value")

    @property
    def field_type(self) -> str:
        return self._field_type

    @property
    def option_id(self) -> str | None:
        return self._option_id

    @property
    def selected(self) -> bool | None:
        return self._selected

    @property
    def text_value(self) -> str | None:
        return self._text_value

    @property
    def number_value(
        self,
    ) -> int | float | None:
        return self._number_value

    @property
    def is_answered(self) -> bool:
        if self._field_type in {
            "single",
            "multi",
        }:
            return self._selected is True

        if self._field_type == "text":
            return (
                self._text_value is not None
                and bool(self._text_value.strip())
            )

        if self._field_type == "number":
            return self._number_value is not None

        return False