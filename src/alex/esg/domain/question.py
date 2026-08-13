class Question:
    def __init__(
            self,
            question_id: str,
            question_code: str,
    ):
        if not isinstance(question_id, str):
            raise TypeError("question_id must be a string")
        if not question_id.strip():
            raise ValueError("question_id cannot be empty")
        if not isinstance(question_code, str):
            raise TypeError("question_code must be a string")
        if not question_code.strip():
            raise ValueError("question_code cannot be empty")

        self.question_id = question_id
        self.question_code = question_code
