class Option:
    def __init__(
        self,
        option_id: str,
        value: str,
        label: str,
    ):
        if not isinstance(option_id, str):
            raise TypeError("option_id must be a string")

        if not option_id.strip():
            raise ValueError("option_id cannot be empty")

        if not isinstance(value, str):
            raise TypeError("value must be a string")

        if not value.strip():
            raise ValueError("value cannot be empty")

        if not isinstance(label, str):
            raise TypeError("label must be a string")

        if not label.strip():
            raise ValueError("label cannot be empty")

        self.option_id = option_id
        self.value = value
        self.label = label