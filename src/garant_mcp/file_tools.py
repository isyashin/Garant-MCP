"""File management tools for Garant MCP Server."""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

RESULTS_DIR = Path("results")
CASES_DIR = RESULTS_DIR / "cases"
TEMPLATES_DIR = RESULTS_DIR / "templates"
DOCUMENTS_DIR = RESULTS_DIR / "documents"
PRACTICE_DIR = RESULTS_DIR / "practice"
CLIENT_DATA_DIR = RESULTS_DIR / "client_data"
OUTPUT_DIR = RESULTS_DIR / "output"

# Ensure directories exist
for dir_path in [CASES_DIR, TEMPLATES_DIR, DOCUMENTS_DIR, 
                 PRACTICE_DIR, CLIENT_DATA_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def save_document(content: str, filename: str, category: str = "output") -> str:
    """Save document to appropriate directory."""
    dirs = {
        "cases": CASES_DIR,
        "templates": TEMPLATES_DIR,
        "documents": DOCUMENTS_DIR,
        "practice": PRACTICE_DIR,
        "client": CLIENT_DATA_DIR,
        "output": OUTPUT_DIR,
    }
    
    target_dir = dirs.get(category, OUTPUT_DIR)
    filepath = target_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(filepath)


def load_document(filename: str, category: str = "output") -> Optional[str]:
    """Load document from appropriate directory."""
    dirs = {
        "cases": CASES_DIR,
        "templates": TEMPLATES_DIR,
        "documents": DOCUMENTS_DIR,
        "practice": PRACTICE_DIR,
        "client": CLIENT_DATA_DIR,
        "output": OUTPUT_DIR,
    }
    
    target_dir = dirs.get(category, OUTPUT_DIR)
    filepath = target_dir / filename
    
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def list_documents(category: str = "output") -> list[str]:
    """List documents in category directory."""
    dirs = {
        "cases": CASES_DIR,
        "templates": TEMPLATES_DIR,
        "documents": DOCUMENTS_DIR,
        "practice": PRACTICE_DIR,
        "client": CLIENT_DATA_DIR,
        "output": OUTPUT_DIR,
    }
    
    target_dir = dirs.get(category, OUTPUT_DIR)
    
    if not target_dir.exists():
        return []
    
    return [f.name for f in target_dir.iterdir() if f.is_file()]


def create_case_folder(case_name: str) -> str:
    """Create folder for specific case."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{timestamp}_{case_name}"
    case_path = CASES_DIR / folder_name
    case_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (case_path / "documents").mkdir(exist_ok=True)
    (case_path / "practice").mkdir(exist_ok=True)
    (case_path / "output").mkdir(exist_ok=True)
    
    return str(case_path)


def copy_template(template_name: str, destination: str) -> str:
    """Copy template to destination."""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found")
    
    dest_path = Path(destination)
    shutil.copy2(template_path, dest_path)
    
    return str(dest_path)


def create_log(case_name: str, action: str, details: str = "") -> None:
    """Create work log for case."""
    log_dir = RESULTS_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{case_name}.log"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {action}\n")
        if details:
            f.write(f"  Details: {details}\n")
        f.write("\n")
