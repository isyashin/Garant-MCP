"""MCP Tools for Garant API."""

import json
import logging
from pathlib import Path
from typing import Optional
from .client import GarantClient
from .config import Config
from .file_tools import (
    save_document,
    load_document,
    list_documents,
    create_case_folder,
    copy_template,
    create_log,
    save_to_case,
    list_cases,
    get_latest_case,
    copy_docx_to_case,
    CASES_ROOT,
)
from .template_manager import (
    find_template,
    list_templates,
    render_template,
    copy_template_to_case,
)

logger = logging.getLogger(__name__)


def _get_client() -> GarantClient:
    """Get a fresh GarantClient instance."""
    return GarantClient()


async def search_documents(
    text: str,
    env: str = "internet",
    sort: int = 0,
    sort_order: int = 0,
    page: int = 1,
    is_query: bool = False,
) -> str:
    """
    Search for legal documents in Garant database.

    Args:
        text: Search query (max 16KB). Can be plain text or query language expression.
        env: Search environment - 'internet' (main) or 'arbitr' (court practice).
        sort: Sort type - 0=relevance, 1=date, 2=last modified, 3=legal force.
        sort_order: Sort order - 0=descending, 1=ascending.
        page: Page number (50 documents per page).
        is_query: Use query language (e.g., 'MorphoText(НДФЛ) & Type(Приказ)').

    Returns:
        JSON string with search results including documents list and total pages.
    """
    try:
        result = await _get_client().search_documents(
            text=text,
            env=env,
            sort=sort,
            sort_order=sort_order,
            page=page,
            is_query=is_query,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Search error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_document_info(topic: int) -> str:
    """
    Get detailed information about a specific document.

    Args:
        topic: Internal document ID (integer).

    Returns:
        JSON string with document metadata (name, status, type, dates, etc.).
    """
    try:
        result = await _get_client().get_document_info(topic)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Document info error for topic {topic}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_document_snippets(
    text: str,
    topic: int,
) -> str:
    """
    Get text snippets (occurrences) within a specific document.

    Args:
        text: Search text to find within the document.
        topic: Document ID to search in.

    Returns:
        JSON string with snippets showing relevance and context.
    """
    try:
        result = await _get_client().get_snippets(text=text, topic=topic)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Snippets error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def create_legal_document(
    text: str,
    base_url: str = "https://internet.garant.ru",
) -> str:
    """
    Create a legal document with hyperlinks to laws.

    Automatically finds references to laws and adds clickable links.

    Args:
        text: Document text (plain text or HTML, max 20MB).
        base_url: Base URL for generated links (default: internet.garant.ru).

    Returns:
        HTML string with embedded hyperlinks to relevant laws.
    """
    try:
        result = await _get_client().create_hyperlinks(text=text, base_url=base_url)
        return result.get("text", "")
    except Exception as e:
        logger.error(f"Hyperlinks error: {e}")
        return f"Error: {str(e)}"


async def check_document_updates(
    topics: list[int],
    mod_date: str,
    need_events: bool = True,
) -> str:
    """
    Check if documents have been modified since a specific date.

    Args:
        topics: List of document IDs to check (max 100).
        mod_date: Check for changes since this date (YYYY-MM-DD, not earlier than 2018-01-01).
        need_events: Include detailed modification history.

    Returns:
        JSON string with modification status for each document.
    """
    try:
        result = await _get_client().find_modified(
            topics=topics,
            mod_date=mod_date,
            need_events=need_events,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Modified error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def export_document_rtf(topic: int) -> str:
    """
    Export a document to RTF format.

    Args:
        topic: Document ID to export.

    Returns:
        Path to downloaded RTF file.
    """
    try:
        output_dir = Path(Config.EXPORT_DIR)
        output_dir.mkdir(exist_ok=True)
        path = await _get_client().export_document_rtf(topic, output_dir)
        return str(path)
    except Exception as e:
        logger.error(f"Export RTF error for topic {topic}: {e}")
        return f"Error: {str(e)}"


async def export_document_pdf(topic: int) -> str:
    """
    Export a document to PDF format.

    Args:
        topic: Document ID to export.

    Returns:
        Path to downloaded PDF file.
    """
    try:
        output_dir = Path(Config.EXPORT_DIR)
        output_dir.mkdir(exist_ok=True)
        path = await _get_client().export_document_pdf(topic, output_dir)
        return str(path)
    except Exception as e:
        logger.error(f"Export PDF error for topic {topic}: {e}")
        return f"Error: {str(e)}"


async def export_document_odt(topic: int) -> str:
    """
    Export a document to ODT format.

    Args:
        topic: Document ID to export.

    Returns:
        Path to downloaded ODT file.
    """
    try:
        output_dir = Path(Config.EXPORT_DIR)
        output_dir.mkdir(exist_ok=True)
        path = await _get_client().export_document_odt(topic, output_dir)
        return str(path)
    except Exception as e:
        logger.error(f"Export ODT error for topic {topic}: {e}")
        return f"Error: {str(e)}"


async def export_document_html(topic: int) -> str:
    """
    Export a document to HTML format.

    Args:
        topic: Document ID to export.

    Returns:
        JSON string with HTML pages of the document.
    """
    try:
        result = await _get_client().export_document_html(topic)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Export HTML error for topic {topic}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def export_block_html(topic: int, entry: int) -> str:
    """
    Export a specific block (article, paragraph) to HTML.

    Args:
        topic: Document ID.
        entry: Block ID (e.g., 36 for Article 36, 3601 for paragraph 1 of Article 36).

    Returns:
        JSON string with HTML content of the block.
    """
    try:
        result = await _get_client().export_block_html(topic, entry)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Export block error for topic {topic} entry {entry}: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_prime_categories() -> str:
    """
    Get PRIME news categories.

    Returns:
        JSON string with category tree.
    """
    try:
        result = await _get_client().get_prime_categories()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"PRIME categories error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_prime_news(
    categories: list[int],
    from_date: str,
    to_date: str,
    sort: int = 1,
) -> str:
    """
    Get PRIME news feed.

    Args:
        categories: List of category IDs from get_prime_categories.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD, max 10 days from from_date).
        sort: Sort order - 1=by news date (default), 2=by document adoption date.

    Returns:
        JSON string with news items.
    """
    try:
        result = await _get_client().get_prime_news(
            categories=categories,
            from_date=from_date,
            to_date=to_date,
            sort=sort,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"PRIME news error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def search_judicial_practice(
    text: str,
    count: int = 10,
    kind: Optional[list[str]] = None,
) -> str:
    """
    Search judicial practice (Sutyazhnik).

    Args:
        text: Search query text (1-1000 characters).
        count: Number of results to return.
        kind: Document types - ['301'] for courts, ['302'] for arbitration, ['303'] for company cases.

    Returns:
        JSON string with judicial practice documents, norms, and court decisions.
    """
    try:
        if kind is None:
            kind = ["301", "302"]
        result = await _get_client().search_judicial_practice(
            text=text,
            count=count,
            kind=kind,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Sutyazhnik error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_usage_limits() -> str:
    """
    Check remaining API usage limits.

    Returns:
        JSON string with remaining quotas for all endpoint types.
    """
    try:
        result = await _get_client().get_limits()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Limits error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def download_image(object_id: int) -> str:
    """
    Download an image from a document.

    Args:
        object_id: Image object ID (found in HTML content).

    Returns:
        Path to downloaded image file.
    """
    try:
        output_dir = Path(Config.EXPORT_DIR)
        output_dir.mkdir(exist_ok=True)
        path = await _get_client().get_image(object_id, output_dir)
        return str(path)
    except Exception as e:
        logger.error(f"Image error for object_id {object_id}: {e}")
        return f"Error: {str(e)}"


async def download_formula(text: str) -> str:
    """
    Download a formula as an image.

    Args:
        text: Formula text.

    Returns:
        Path to downloaded formula image.
    """
    try:
        output_dir = Path(Config.EXPORT_DIR)
        output_dir.mkdir(exist_ok=True)
        path = await _get_client().get_formula(text, output_dir)
        return str(path)
    except Exception as e:
        logger.error(f"Formula error: {e}")
        return f"Error: {str(e)}"


async def save_text_document(
    content: str, filename: str, category: str = "output"
) -> str:
    """Save text document to results directory.

    Args:
        content: Document content.
        filename: File name.
        category: Directory category (cases/templates/documents/practice/client/output).

    Returns:
        Path to saved file.
    """
    try:
        filepath = save_document(content, filename, category)
        create_log("general", f"Saved document: {filename}", f"Category: {category}")
        return f"Document saved to: {filepath}"
    except Exception as e:
        logger.error(f"Save document error: {e}")
        return f"Error: {str(e)}"


async def load_text_document(filename: str, category: str = "output") -> str:
    """Load text document from results directory.

    Args:
        filename: File name.
        category: Directory category.

    Returns:
        Document content or error message.
    """
    try:
        content = load_document(filename, category)
        if content is None:
            return f"Document '{filename}' not found in {category}"
        return content
    except Exception as e:
        logger.error(f"Load document error: {e}")
        return f"Error: {str(e)}"


async def list_saved_documents(category: str = "output") -> str:
    """List documents in results directory.

    Args:
        category: Directory category.

    Returns:
        JSON string with document list.
    """
    try:
        documents = list_documents(category)
        return json.dumps(
            {"category": category, "documents": documents, "count": len(documents)},
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        logger.error(f"List documents error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def create_case(case_name: str) -> str:
    """Create folder structure for a new case with human-readable Russian names.

    Creates structure:
        кейсы/
        └── описание_кейса_YYYY-MM-DD/
            ├── исходные данные/          # User input and documents
            ├── результат/                 # Final documents (DOCX, PDF)
            └── служебное для агента/      # Research and intermediate results

    Args:
        case_name: Short description in Russian (e.g., 'Возврат_автомобиля_дилеру').

    Returns:
        Path to created case folder and structure description.
    """
    try:
        case_path = create_case_folder(case_name)
        create_log(case_name, "Case created", f"Path: {case_path}")

        # Return detailed info about structure
        return (
            f"КЕЙС СОЗДАН: {case_path}\n\n"
            f"Структура папок:\n"
            f"├── исходные данные/     - Входные документы и описание запроса\n"
            f"├── результат/           - Готовые документы для клиента (DOCX)\n"
            f"└── служебное для агента/ - Исследования, поиски, промежуточные результаты\n\n"
            f"Для сохранения файлов используй save_to_case_tool с case_path='{case_path}'"
        )
    except Exception as e:
        logger.error(f"Create case error: {e}")
        return f"Error: {str(e)}"


async def copy_template_file(template_name: str, destination: str) -> str:
    """Copy template file to destination.

    Args:
        template_name: Source template file name.
        destination: Destination path.

    Returns:
        Path to copied file.
    """
    try:
        dest_path = copy_template(template_name, destination)
        return f"Template copied to: {dest_path}"
    except Exception as e:
        logger.error(f"Copy template error: {e}")
        return f"Error: {str(e)}"


async def save_to_case_tool(
    content: str,
    case_path: str,
    filename: str,
    subfolder: str = "служебное для агента",
) -> str:
    """Save document to specific case subfolder.

    Args:
        content: Document content.
        case_path: Full path to case folder (e.g., 'кейсы/Возврат_автомобиля_дилеру_2026-06-01').
        filename: File name.
        subfolder: Target subfolder - 'исходные данные', 'результат', or 'служебное для агента'.

    Returns:
        Path to saved file.
    """
    try:
        filepath = save_to_case(content, case_path, filename, subfolder)
        create_log(case_path, f"Saved to {subfolder}: {filename}")
        return f"Document saved to: {filepath}"
    except Exception as e:
        logger.error(f"Save to case error: {e}")
        return f"Error: {str(e)}"


async def list_cases_tool() -> str:
    """List all case folders.

    Returns:
        JSON string with case list.
    """
    try:
        cases = list_cases()
        return json.dumps(
            {
                "cases": cases,
                "count": len(cases),
                "cases_root": str(CASES_ROOT),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        logger.error(f"List cases error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_latest_case_tool() -> str:
    """Get the most recently created case folder.

    Returns:
        Path to latest case folder.
    """
    try:
        latest = get_latest_case()
        if latest is None:
            return "No cases found"
        return f"Latest case: {latest}"
    except Exception as e:
        logger.error(f"Get latest case error: {e}")
        return f"Error: {str(e)}"


async def copy_docx_to_case_tool(
    source_path: str,
    case_path: str,
    new_filename: Optional[str] = None,
) -> str:
    """Copy DOCX file to case result folder.

    Args:
        source_path: Path to source DOCX file.
        case_path: Path to case folder.
        new_filename: Optional new filename for result.

    Returns:
        Path to copied file.
    """
    try:
        dest_path = copy_docx_to_case(source_path, case_path, new_filename)
        return f"DOCX copied to result: {dest_path}"
    except Exception as e:
        logger.error(f"Copy DOCX to case error: {e}")
        return f"Error: {str(e)}"


async def create_case_description(
    case_path: str,
    description: str,
) -> str:
    """Create case description file in 'исходные данные'.

    Args:
        case_path: Path to case folder.
        description: Case description text.

    Returns:
        Path to created file.
    """
    try:
        filepath = save_to_case(
            description,
            case_path,
            "Описание_запроса.txt",
            "исходные данные",
        )
        return f"Case description saved: {filepath}"
    except Exception as e:
        logger.error(f"Create case description error: {e}")
        return f"Error: {str(e)}"


async def find_template_by_request_tool(request: str) -> str:
    """Find best matching DOCX template by user request.

    Args:
        request: User request or case description.

    Returns:
        JSON with matched template name and description.
    """
    try:
        template = find_template(request)
        if template is None:
            return json.dumps(
                {"error": "No templates available"},
                ensure_ascii=False,
            )
        return json.dumps(
            {
                "template": template["name"],
                "description": template["description"],
                "placeholders": template.get("placeholders", []),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        logger.error(f"Find template error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def list_templates_tool() -> str:
    """List available DOCX templates.

    Returns:
        JSON with template list.
    """
    try:
        templates = list_templates()
        return json.dumps(
            {"templates": [t["name"] for t in templates], "count": len(templates)},
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        logger.error(f"List templates error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def render_docx_template_tool(
    template_name: str,
    output_path: str,
    placeholders_json: str,
) -> str:
    """Render DOCX template by replacing placeholders.

    Args:
        template_name: Name of template file in results/templates.
        output_path: Path where to save rendered DOCX.
        placeholders_json: JSON string with placeholder mapping.

    Returns:
        Path to rendered DOCX.
    """
    try:
        placeholders = json.loads(placeholders_json)
        path = render_template(template_name, Path(output_path), placeholders)
        return f"Rendered DOCX: {path}"
    except Exception as e:
        logger.error(f"Render template error: {e}")
        return f"Error: {str(e)}"


async def copy_template_to_case_tool(
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
    try:
        path = copy_template_to_case(template_name, case_path, new_filename)
        return f"Template copied to case result: {path}"
    except Exception as e:
        logger.error(f"Copy template to case error: {e}")
        return f"Error: {str(e)}"


async def search_and_cite_tool(
    query: str,
    topic: Optional[int] = None,
    snippet_count: int = 3,
) -> str:
    """Search legislation and format citations without paid export.

    Uses search_documents or get_document_snippets to find relevant norms,
    then formats citations with links to garant.ru.

    Args:
        query: Search query.
        topic: Optional specific document ID to search within.
        snippet_count: Number of snippets to request when topic is given.

    Returns:
        JSON with search results and formatted citations.
    """
    try:
        client = _get_client()
        results: list[dict] = []

        if topic is not None:
            snippets = await client.get_snippets(text=query, topic=topic)
            for item in snippets.get("snippets", [])[:snippet_count]:
                entry = item.get("entry")
                ancestors = item.get("ancestors", [])
                title = ancestors[-1]["title"] if ancestors else ""
                results.append(
                    {
                        "type": "snippet",
                        "topic": topic,
                        "entry": entry,
                        "title": title,
                        "url": f"https://internet.garant.ru/#/document/{topic}/entry/{entry}",
                    }
                )
        else:
            search_result = await client.search_documents(text=query, page=1)
            for doc in search_result.get("documents", [])[:snippet_count]:
                topic_id = doc.get("topic")
                results.append(
                    {
                        "type": "document",
                        "topic": topic_id,
                        "name": doc.get("name"),
                        "url": f"https://internet.garant.ru/#/document/{topic_id}",
                    }
                )

        return json.dumps(
            {
                "query": query,
                "topic": topic,
                "results": results,
                "note": "Use these URLs as hyperlinks in documents. Avoid export_* tools unless user explicitly requests a file.",
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as e:
        logger.error(f"Search and cite error: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)
