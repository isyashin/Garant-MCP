"""File management tools for Garant MCP Server."""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

# Основная папка для кейсов (на русском, понятная человеку)
CASES_ROOT = Path("кейсы")

# Старые папки (для обратной совместимости)
RESULTS_DIR = Path("results")
CASES_DIR = RESULTS_DIR / "cases"
TEMPLATES_DIR = RESULTS_DIR / "templates"
DOCUMENTS_DIR = RESULTS_DIR / "documents"
PRACTICE_DIR = RESULTS_DIR / "practice"
CLIENT_DATA_DIR = RESULTS_DIR / "client_data"
OUTPUT_DIR = RESULTS_DIR / "output"

# Ensure old directories exist (backward compatibility)
for dir_path in [CASES_DIR, TEMPLATES_DIR, DOCUMENTS_DIR, 
                 PRACTICE_DIR, CLIENT_DATA_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(name: str) -> str:
    """Sanitize case name for use in folder name."""
    # Replace spaces with underscores
    sanitized = name.strip().replace(' ', '_')
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '')
    return sanitized


def create_case_folder(case_name: str) -> str:
    """Create folder structure for a new case.
    
    Structure:
        кейсы/
        └── описание_кейса_YYYY-MM-DD/
            ├── исходные данные/          # User input, documents, case description
            ├── результат/                 # Final documents for client (DOCX, PDF)
            └── служебное для агента/      # Research, logs, intermediate results
    
    Args:
        case_name: Short case description in Russian (e.g., "Возврат_автомобиля_дилеру")
    
    Returns:
        Path to created case folder.
    """
    # Sanitize case name
    sanitized_name = _sanitize_filename(case_name)
    
    # Create folder name: описание_YYYY-MM-DD
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{sanitized_name}_{date_str}"
    
    # Create case path
    case_path = CASES_ROOT / folder_name
    case_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories with Russian names
    (case_path / "исходные данные").mkdir(exist_ok=True)
    (case_path / "результат").mkdir(exist_ok=True)
    (case_path / "служебное для агента").mkdir(exist_ok=True)
    
    return str(case_path)


def get_case_subfolder(case_path: str, subfolder: str) -> Path:
    """Get path to case subfolder.
    
    Args:
        case_path: Path to case folder.
        subfolder: One of: 'исходные данные', 'результат', 'служебное для агента'.
    
    Returns:
        Path to subfolder.
    """
    case = Path(case_path)
    return case / subfolder


def save_to_case(content: str, case_path: str, filename: str, 
                 subfolder: str = "служебное для агента") -> str:
    """Save document to case subfolder.
    
    Args:
        content: Document content.
        case_path: Path to case folder.
        filename: File name.
        subfolder: Target subfolder (default: 'служебное для агента').
    
    Returns:
        Path to saved file.
    """
    target_dir = get_case_subfolder(case_path, subfolder)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = target_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(filepath)


def save_document(content: str, filename: str, category: str = "output") -> str:
    """Save document to old results directory (backward compatibility).
    
    For new cases, use save_to_case() instead.
    """
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
    """Load document from old results directory (backward compatibility)."""
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
    """List documents in old results directory (backward compatibility)."""
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


def list_cases() -> list[str]:
    """List all case folders.
    
    Returns:
        List of case folder names.
    """
    if not CASES_ROOT.exists():
        return []
    
    return [d.name for d in CASES_ROOT.iterdir() if d.is_dir()]


def get_latest_case() -> Optional[str]:
    """Get path to most recently created case folder.
    
    Returns:
        Path to latest case or None.
    """
    cases = list_cases()
    if not cases:
        return None
    
    # Sort by modification time
    case_paths = [CASES_ROOT / c for c in cases]
    latest = max(case_paths, key=lambda p: p.stat().st_mtime)
    return str(latest)


def copy_template(template_name: str, destination: str) -> str:
    """Copy template to destination."""
    template_path = TEMPLATES_DIR / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template {template_name} not found")
    
    dest_path = Path(destination)
    shutil.copy2(template_path, dest_path)
    
    return str(dest_path)


def create_log(case_name: str, action: str, details: str = "") -> None:
    """Create work log for case.
    
    For new cases, saves to 'служебное для агента/log.txt'
    """
    # Try to find case folder (exact match at start of name)
    sanitized = _sanitize_filename(case_name)
    case_path = None
    
    if CASES_ROOT.exists():
        for case_dir in CASES_ROOT.iterdir():
            if case_dir.name.startswith(sanitized):
                case_path = case_dir
                break
    
    if case_path:
        log_dir = case_path / "служебное для агента"
    else:
        log_dir = RESULTS_DIR / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {action}\n")
        if details:
            f.write(f"  Details: {details}\n")
        f.write("\n")


def copy_docx_to_case(source_path: str, case_path: str, 
                      new_filename: str = None) -> str:
    """Copy DOCX file to case result folder.
    
    Args:
        source_path: Path to source DOCX file.
        case_path: Path to case folder.
        new_filename: Optional new filename.
    
    Returns:
        Path to copied file.
    """
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source_path}")
    
    result_dir = get_case_subfolder(case_path, "результат")
    result_dir.mkdir(parents=True, exist_ok=True)
    
    if new_filename:
        dest = result_dir / new_filename
    else:
        dest = result_dir / source.name
    
    shutil.copy2(source, dest)
    return str(dest)
