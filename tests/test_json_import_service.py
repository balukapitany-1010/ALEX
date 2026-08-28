import json
import pytest
from alex.esg.services.json_import_service import JsonImportService


def test_json_import_service_loads_json(tmp_path):
    file_path = tmp_path / "test.json"

    data = {
        "spec_version": "2.1",
        "name": "Teszt",
    }

    file_path.write_text(json.dumps(data),encoding="utf-8",)

    service = JsonImportService()

    result = service.load_file(file_path)

    assert result == data


def test_json_import_service_rejects_missing_file(tmp_path):
    service = JsonImportService()

    file_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        service.load_file(file_path)


def test_json_import_service_rejects_non_json_file(tmp_path):
    file_path = tmp_path / "test.txt"

    file_path.write_text("test",encoding="utf-8")

    service = JsonImportService()

    with pytest.raises(ValueError,match=r"file must have \.json extension"):
        service.load_file(file_path)


def test_json_import_service_rejects_invalid_json(tmp_path):
    file_path = tmp_path / "test.json"

    file_path.write_text("{ invalid json",encoding="utf-8")

    service = JsonImportService()

    with pytest.raises(ValueError,match="invalid JSON",):
        service.load_file(file_path)


def test_json_import_service_rejects_array_root(tmp_path):
    file_path = tmp_path / "test.json"

    file_path.write_text("[1, 2, 3]",encoding="utf-8",)

    service = JsonImportService()

    with pytest.raises(ValueError,match="JSON root must be an object"):
        service.load_file(file_path)