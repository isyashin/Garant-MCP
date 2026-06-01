"""Tests for file management tools."""

import pytest
from pathlib import Path
import shutil

from garant_mcp.file_tools import (
    save_document,
    load_document,
    list_documents,
    create_case_folder,
    copy_template,
    create_log,
    RESULTS_DIR,
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
        """Test creating case folder structure."""
        case_path = create_case_folder("test_case")
        path = Path(case_path)
        
        assert path.exists()
        assert (path / "documents").exists()
        assert (path / "practice").exists()
        assert (path / "output").exists()
        
        # Cleanup
        shutil.rmtree(path, ignore_errors=True)
    
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
        log_file = log_dir / "test_case.log"
        
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test action" in content
        assert "Test details" in content
        
        # Cleanup
        log_file.unlink()
