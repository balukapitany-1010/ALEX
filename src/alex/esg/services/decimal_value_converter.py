from decimal import (
    Decimal,
    InvalidOperation,
    ROUND_HALF_UP,
    localcontext,
)

class DecimalValueConverter:
    SCALE = Decimal("0.0001")
    MAX_VALUE = Decimal("99999999999999.9999")

    @classmethod
    def to_decimal_18_4(
        cls,
        value,
    ) -> Decimal | None:
        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            raise TypeError("boolean is not a valid number")

        text = str(value).strip()

        if not text:
            return None


        text = text.replace(
            ",",
            ".",
        )

        try:
            decimal_value = Decimal(text)

        except InvalidOperation as error:
            raise ValueError(f"invalid decimal value: {value}") from error

        if not decimal_value.is_finite():
            raise ValueError(f"decimal value must be finite: {value}")

        with localcontext() as context:
            context.prec = 40

            rounded = (
                decimal_value.quantize(
                    cls.SCALE,
                    rounding=ROUND_HALF_UP,
                )
            )

        if abs(rounded) > cls.MAX_VALUE:
            raise ValueError("number exceeds decimal(18,4) " f"range: {value}")
        return rounded