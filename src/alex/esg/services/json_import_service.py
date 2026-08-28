import json
from pathlib import Path
from typing import Any


class JsonImportService:
    def load_file(
        self,
        file_path: str | Path,
    ) -> dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        if not path.is_file():
            raise ValueError(f"path is not a file: {path}")

        if path.suffix.lower() != ".json":
            raise ValueError("file must have .json extension")

        try:
            with path.open("r",encoding="utf-8-sig",) as file:
                data = json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON: {error}") from error

        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")

        return data

    def detect_document_type(
            self,
            data: dict[str, Any],
    ) -> str:
        if not isinstance(data, dict):
            raise TypeError("data must be a dictionary")

        if ("pages" in data and "locale" in data and "spec_version" in data):
            return "questionnaire_definition"

        if ("submissions" in data and "spec_version" in data):
            return "submission_batch"

        raise ValueError("unsupported JSON document structure")

    def validate_questionnaire_definition(
            self,
            data: dict[str, Any],
    ) -> None:
        if self.detect_document_type(data) != "questionnaire_definition":
            raise ValueError("JSON is not a questionnaire definition")

        spec_version = data.get("spec_version")

        if not isinstance(spec_version, str) or not spec_version.strip():
            raise ValueError("spec_version is required")

        locale = data.get("locale")

        if not isinstance(locale, str) or not locale.strip():
            raise ValueError("locale is required")

        pages = data.get("pages")

        if not isinstance(pages, list) or not pages:
            raise ValueError( "pages must be a non-empty list")

        question_ids: set[str] = set()

        for page in pages:
            elements = page.get("elements", [])

            if not isinstance(elements, list):
                raise ValueError("page elements must be a list")

            for element in elements:
                question_id = element.get("ID")
                question_code = element.get("name")

                if not isinstance(question_id, str) or not question_id.strip():
                    raise ValueError("question ID is required")

                if not isinstance(question_code, str) or not question_code.strip():
                    raise ValueError(f"question name is required for ID {question_id}")

                if question_id in question_ids:
                    raise ValueError(f"duplicate question ID: {question_id}")

                question_ids.add(question_id)

    def validate_submission_batch(
            self,
            data: dict[str, Any],
    ) -> None:
        if self.detect_document_type(data) != "submission_batch":
            raise ValueError("JSON is not a submission batch")

        spec_version = data.get("spec_version")

        if not isinstance(spec_version, str) or not spec_version.strip():
            raise ValueError("spec_version is required")

        submissions = data.get("submissions")

        if not isinstance(submissions, list) or not submissions:
            raise ValueError("submissions must be a non-empty list")

        for submission_index, submission in enumerate(submissions):
            response = submission.get("response")

            if not isinstance(response, dict):
                raise ValueError(f"submission {submission_index} has no valid response")

            questions = response.get("questions")

            if not isinstance(questions, list):
                raise ValueError(f"submission {submission_index} questions must be a list")

            technical_ids: set[str] = set()

            for question in questions:
                technical_id = question.get("id")
                question_code = question.get("question_id")

                if not isinstance(technical_id, str) or not technical_id.strip():
                    raise ValueError("response question id is required")

                if not isinstance(question_code, str) or not question_code.strip():
                    raise ValueError(f"question_id is required for {technical_id}")

                if technical_id in technical_ids:
                    raise ValueError(f"duplicate response question id: {technical_id}")

                technical_ids.add(technical_id)

                fields = question.get("fields")

                if not isinstance(fields, list):
                    raise ValueError(f"fields must be a list for question {technical_id}")