

class Questionnaire:
    def __init__(
        self,
        questionnaire_code: str,
        spec_version: str,
        locale: str,
    ):
        if not isinstance(questionnaire_code, str):
            raise TypeError("questionnaire_code must be a string")

        if not questionnaire_code.strip():
            raise ValueError("questionnaire_code cannot be empty")

        if not isinstance(spec_version, str):
            raise TypeError("spec_version must be a string")

        if not spec_version.strip():
            raise ValueError("spec_version cannot be empty")

        if not isinstance(locale, str):
            raise TypeError("locale must be a string")

        if not locale.strip():
            raise ValueError("locale cannot be empty")

        self.questionnaire_code = questionnaire_code
        self.spec_version = spec_version
        self.locale = locale

    @property
    def questionnaire_key(self) -> str:
        return (
            f"{self.questionnaire_code}:"
            f"{self.spec_version}:"
            f"{self.locale}"
        )