"""Tests for file management tools."""

import pytest
from pathlib import Path
import shutil

from garant_mcp.file_tools import (
    save_document,
    load_document,
    list_documents,
    create_case_folder,
    save_to_case,
    list_cases,
    get_latest_case,
    copy_template,
    create_log,
    RESULTS_DIR,
    CASES_ROOT,
)


class TestFileTools:
    """Test file management functionality."""

    def test_save_and_load_document(self, tmp_path):
        """Test saving and loading documents."""
        # Save document
        content = "Test document content"
        filepath = save_document(content, "test_doc.txt", "output")

        assert Path(filepath).exists()

        # Load document
        loaded = load_document("test_doc.txt", "output")
        assert loaded == content

    def test_load_nonexistent_document(self):
        """Test loading non-existent document."""
        result = load_document("nonexistent.txt", "output")
        assert result is None

    def test_list_documents(self):
        """Test listing documents."""
        # Save a test document
        save_document("test", "list_test.txt", "output")

        # List documents
        docs = list_documents("output")
        assert "list_test.txt" in docs

    def test_create_case_folder(self):
        """Test creating case folder structure with Russian names."""
        case_path = create_case_folder("Тест_кейса")
        path = Path(case_path)

        assert path.exists()
        # Check Russian subfolders
        assert (path / "исходные данные").exists()
        assert (path / "результат").exists()
        assert (path / "служебное для агента").exists()

        # Check that case is under кейсы/
        assert CASES_ROOT in path.parents or path.parent == CASES_ROOT

        # Cleanup
        shutil.rmtree(path, ignore_errors=True)

    def test_save_to_case(self):
        """Test saving to case subfolder."""
        case_path = create_case_folder("Тест_сохранения")

        # Save to different subfolders
        filepath1 = save_to_case(
            "Test content 1", case_path, "test1.txt", "исходные данные"
        )
        filepath2 = save_to_case("Test content 2", case_path, "test2.txt", "результат")
        filepath3 = save_to_case(
            "Test content 3", case_path, "test3.txt", "служебное для агента"
        )

        assert Path(filepath1).exists()
        assert Path(filepath2).exists()
        assert Path(filepath3).exists()

        # Check content
        assert Path(filepath1).read_text(encoding="utf-8") == "Test content 1"

        # Cleanup
        shutil.rmtree(case_path, ignore_errors=True)

    def test_list_cases(self):
        """Test listing cases."""
        # Create a test case
        case_path = create_case_folder("Тест_списка")

        cases = list_cases()
        assert len(cases) >= 1
        assert any("Тест_списка" in c for c in cases)

        # Cleanup
        shutil.rmtree(case_path, ignore_errors=True)

    def test_get_latest_case(self):
        """Test getting latest case."""
        # Create a test case
        case_path = create_case_folder("Тест_последний")

        latest = get_latest_case()
        assert latest is not None
        assert "Тест_последний" in latest

        # Cleanup
        shutil.rmtree(case_path, ignore_errors=True)

    def test_copy_template(self, tmp_path):
        """Test copying template."""
        # Create a test template
        template_dir = RESULTS_DIR / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        template_file = template_dir / "test_template.txt"
        template_file.write_text("Template content", encoding="utf-8")

        # Copy template
        dest = tmp_path / "copied_template.txt"
        result = copy_template("test_template.txt", str(dest))

        assert Path(result).exists()
        assert Path(result).read_text(encoding="utf-8") == "Template content"

        # Cleanup
        template_file.unlink()

    def test_copy_nonexistent_template(self):
        """Test copying non-existent template."""
        with pytest.raises(FileNotFoundError):
            copy_template("nonexistent.txt", "/tmp/dest.txt")

    def test_create_log(self):
        """Test creating log."""
        create_log("test_case", "Test action", "Test details")

        log_dir = RESULTS_DIR / "logs"
        log_file = log_dir / "log.txt"

        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test action" in content
        assert "Test details" in content

        # Cleanup
        log_file.unlink()
