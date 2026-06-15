"""Template management for Garant lawyer agent."""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path("results/templates")
INDEX_FILE = TEMPLATES_DIR / "templates_index.json"


def _load_index() -> dict:
    """Load templates index from JSON."""
    if not INDEX_FILE.exists():
        return {"version": "1.0.0", "templates": []}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_template(request: str) -> Optional[dict]:
    """Find best matching template by user request keywords.

    Args:
        request: User request or case description.

    Returns:
        Template info dict or None if no match found.
    """
    index = _load_index()
    request_lower = request.lower()
    best_match: Optional[dict] = None
    best_score = 0

    for template in index.get("templates", []):
        score = sum(
            1
            for keyword in template.get("keywords", [])
            if keyword.lower() in request_lower
        )
        if score > best_score:
            best_score = score
            best_match = template

    if best_match is None and index.get("templates"):
        best_match = index["templates"][0]

    if best_match:
        logger.info(
            f"Template match for '{request[:50]}...': "
            f"{best_match['name']} (score={best_score})"
        )

    return best_match


def list_templates() -> list[dict]:
    """Return list of available templates."""
    index = _load_index()
    return index.get("templates", [])


def get_template_path(template_name: str) -> Path:
    """Return full path to template file."""
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path


def render_template(
    template_name: str,
    output_path: Path,
    placeholders: dict[str, str],
) -> Path:
    """Render DOCX template by replacing placeholders.

    Placeholders in template are wrapped in curly braces, e.g. {ФИО_истец}.

    Args:
        template_name: Name of template file in results/templates.
        output_path: Where to save rendered document.
        placeholders: Mapping placeholder name -> value.

    Returns:
        Path to rendered DOCX.
    """
    try:
        from docx import Document
    except ImportError as e:
        raise RuntimeError("python-docx is required for rendering templates") from e

    template_path = get_template_path(template_name)
    doc = Document(str(template_path))

    def replace_in_text(text: str) -> str:
        for key, value in placeholders.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        if paragraph.runs:
            full_text = "".join(run.text for run in paragraph.runs)
            new_text = replace_in_text(full_text)
            if new_text != full_text:
                # Clear and set new text preserving style of first run
                first_run = paragraph.runs[0]
                first_run.text = new_text
                for run in paragraph.runs[1:]:
                    run.text = ""

    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    if paragraph.runs:
                        full_text = "".join(run.text for run in paragraph.runs)
                        new_text = replace_in_text(full_text)
                        if new_text != full_text:
                            first_run = paragraph.runs[0]
                            first_run.text = new_text
                            for run in paragraph.runs[1:]:
                                run.text = ""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    logger.info(f"Rendered template {template_name} to {output_path}")
    return output_path


def copy_template_to_case(
    template_name: str,
    case_path: str,
    new_filename: Optional[str] = None,
) -> str:
    """Copy template DOCX to case result folder.

    Args:
        template_name: Template file name.
        case_path: Path to case folder.
        new_filename: Optional new filename.

    Returns:
        Path to copied template.
    """
    import shutil

    template_path = get_template_path(template_name)
    case = Path(case_path)
    result_dir = case / "результат"
    result_dir.mkdir(parents=True, exist_ok=True)

    dest = result_dir / (new_filename or template_path.name)
    shutil.copy2(template_path, dest)
    return str(dest)
