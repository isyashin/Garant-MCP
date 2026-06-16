"""Garant MCP Server - Main entry point."""

import sys
import logging
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .config import Config, BASE_DIR
from .tools import (
    search_documents,
    get_document_info,
    get_document_snippets,
    create_legal_document,
    check_document_updates,
    export_document_rtf,
    export_document_pdf,
    export_document_odt,
    export_document_html,
    export_block_html,
    get_prime_categories,
    get_prime_news,
    search_judicial_practice,
    get_usage_limits,
    download_image,
    download_formula,
    save_text_document,
    load_text_document,
    list_saved_documents,
    create_case,
    copy_template_file,
    save_to_case_tool,
    list_cases_tool,
    get_latest_case_tool,
    copy_docx_to_case_tool,
    create_case_description,
    find_template_by_request_tool,
    list_templates_tool,
    render_docx_template_tool,
    copy_template_to_case_tool,
    search_and_cite_tool,
)
from .resources import (
    get_document_resource,
    get_limits_resource,
    get_prime_categories_resource,
)
from .prompts import (
    legal_complaint_template,
    contract_review_template,
    document_analysis_template,
)

# Configure logging
log_dir = BASE_DIR / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "garant-mcp.log"

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Root logger: capture everything from all modules
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))

# Stream handler for stderr
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(formatter)
root_logger.addHandler(stream_handler)

# File handler for persistent logs
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("garant-mcp")


# === Tools Registration ===


@mcp.tool()
async def search_documents_tool(
    text: str,
    env: str = "internet",
    sort: int = 0,
    sort_order: int = 0,
    page: int = 1,
    is_query: bool = False,
) -> str:
    """Search for legal documents in Garant database."""
    return await search_documents(text, env, sort, sort_order, page, is_query)


@mcp.tool()
async def get_document_info_tool(topic: int) -> str:
    """Get detailed information about a specific document."""
    return await get_document_info(topic)


@mcp.tool()
async def get_document_snippets_tool(text: str, topic: int) -> str:
    """Get text snippets (occurrences) within a specific document."""
    return await get_document_snippets(text, topic)


@mcp.tool()
async def create_legal_document_tool(
    text: str, base_url: str = "https://internet.garant.ru"
) -> str:
    """Create a legal document with hyperlinks to laws."""
    return await create_legal_document(text, base_url)


@mcp.tool()
async def check_document_updates_tool(
    topics: list[int],
    mod_date: str,
    need_events: bool = True,
) -> str:
    """Check if documents have been modified since a specific date."""
    return await check_document_updates(topics, mod_date, need_events)


@mcp.tool()
async def export_document_rtf_tool(topic: int) -> str:
    """Export a document to RTF format."""
    return await export_document_rtf(topic)


@mcp.tool()
async def export_document_pdf_tool(topic: int) -> str:
    """Export a document to PDF format."""
    return await export_document_pdf(topic)


@mcp.tool()
async def export_document_odt_tool(topic: int) -> str:
    """Export a document to ODT format."""
    return await export_document_odt(topic)


@mcp.tool()
async def export_document_html_tool(topic: int) -> str:
    """Export a document to HTML format."""
    return await export_document_html(topic)


@mcp.tool()
async def export_block_html_tool(topic: int, entry: int) -> str:
    """Export a specific block (article, paragraph) to HTML."""
    return await export_block_html(topic, entry)


@mcp.tool()
async def get_prime_categories_tool() -> str:
    """Get PRIME news categories."""
    return await get_prime_categories()


@mcp.tool()
async def get_prime_news_tool(
    categories: list[int],
    from_date: str,
    to_date: str,
    sort: int = 1,
) -> str:
    """Get PRIME news feed."""
    return await get_prime_news(categories, from_date, to_date, sort)


@mcp.tool()
async def search_judicial_practice_tool(
    text: str,
    count: int = 10,
    kind: Optional[list[str]] = None,
) -> str:
    """Search judicial practice (Sutyazhnik)."""
    return await search_judicial_practice(text, count, kind)


@mcp.tool()
async def get_usage_limits_tool() -> str:
    """Check remaining API usage limits."""
    return await get_usage_limits()


@mcp.tool()
async def download_image_tool(object_id: int) -> str:
    """Download an image from a document."""
    return await download_image(object_id)


@mcp.tool()
async def download_formula_tool(text: str) -> str:
    """Download a formula as an image."""
    return await download_formula(text)


@mcp.tool()
async def save_text_document_tool(
    content: str,
    filename: str,
    category: str = "output",
) -> str:
    """Save text document to results directory."""
    return await save_text_document(content, filename, category)


@mcp.tool()
async def load_text_document_tool(
    filename: str,
    category: str = "output",
) -> str:
    """Load text document from results directory."""
    return await load_text_document(filename, category)


@mcp.tool()
async def list_saved_documents_tool(category: str = "output") -> str:
    """List documents in results directory."""
    return await list_saved_documents(category)


@mcp.tool()
async def create_case_tool(case_name: str) -> str:
    """Create folder structure for a new case."""
    return await create_case(case_name)


@mcp.tool()
async def copy_template_file_tool(
    template_name: str,
    destination: str,
) -> str:
    """Copy template file to destination."""
    return await copy_template_file(template_name, destination)


@mcp.tool()
async def save_to_case_tool_wrapper(
    content: str,
    case_path: str,
    filename: str,
    subfolder: str = "служебное для агента",
) -> str:
    """Save document to specific case subfolder.

    Use this to save research results, documents, and intermediate files
    into the correct case folder structure.
    """
    return await save_to_case_tool(content, case_path, filename, subfolder)


@mcp.tool()
async def list_cases_tool_wrapper() -> str:
    """List all case folders.

    Returns JSON with case names and paths.
    """
    return await list_cases_tool()


@mcp.tool()
async def get_latest_case_tool_wrapper() -> str:
    """Get the most recently created case folder.

    Useful when you need to continue working on the last case.
    """
    return await get_latest_case_tool()


@mcp.tool()
async def copy_docx_to_case_tool_wrapper(
    source_path: str,
    case_path: str,
    new_filename: Optional[str] = None,
) -> str:
    """Copy DOCX file to case result folder.

    Use this to move generated DOCX documents into the case result folder.
    """
    return await copy_docx_to_case_tool(source_path, case_path, new_filename)


@mcp.tool()
async def create_case_description_tool(
    case_path: str,
    description: str,
) -> str:
    """Create case description in 'исходные данные' folder.

    Save the original user request and context here.
    """
    return await create_case_description(case_path, description)


@mcp.tool()
async def find_template_by_request_tool_wrapper(request: str) -> str:
    """Find best matching DOCX template by user request."""
    return await find_template_by_request_tool(request)


@mcp.tool()
async def list_templates_tool_wrapper() -> str:
    """List available DOCX templates."""
    return await list_templates_tool()


@mcp.tool()
async def render_docx_template_tool_wrapper(
    template_name: str,
    placeholders_json: str,
    output_path: str = "",
    case_path: str = "",
) -> str:
    """Render DOCX template by replacing placeholders.

    Provide either case_path (recommended) or explicit output_path.
    Template name can be exact filename like 'Претензия.docx' or a keyword
    like 'претензия' — the best matching template will be used.
    """
    return await render_docx_template_tool(
        template_name, placeholders_json, output_path, case_path
    )


@mcp.tool()
async def copy_template_to_case_tool_wrapper(
    template_name: str,
    case_path: str,
    new_filename: Optional[str] = None,
) -> str:
    """Copy template DOCX to case result folder."""
    return await copy_template_to_case_tool(template_name, case_path, new_filename)


@mcp.tool()
async def search_and_cite_tool_wrapper(
    query: str,
    topic: Optional[int] = None,
    snippet_count: int = 3,
) -> str:
    """Search legislation and format citations without paid export.

    Use this instead of export_document_* tools unless user explicitly
    requests a downloaded file.
    """
    return await search_and_cite_tool(query, topic, snippet_count)


# === Resources Registration ===


@mcp.resource("garant://document/{topic}")
async def document_resource(topic: str) -> str:
    """Document metadata resource."""
    return await get_document_resource(int(topic))


@mcp.resource("garant://limits")
async def limits_resource() -> str:
    """API usage limits resource."""
    return await get_limits_resource()


@mcp.resource("garant://prime/categories")
async def prime_categories_resource() -> str:
    """PRIME categories resource."""
    return await get_prime_categories_resource()


# === Prompts Registration ===


@mcp.prompt()
async def legal_complaint() -> str:
    """Template for creating a legal complaint."""
    return await legal_complaint_template()


@mcp.prompt()
async def contract_review() -> str:
    """Template for reviewing a contract."""
    return await contract_review_template()


@mcp.prompt()
async def document_analysis() -> str:
    """Template for analyzing a legal document."""
    return await document_analysis_template()


def main():
    """Main entry point."""
    # Validate configuration
    errors = Config.validate()
    if errors:
        logger.error(f"Configuration errors: {errors}")
        print("Configuration errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    logger.info(
        f"Starting Garant MCP Server | "
        f"Base URL: {Config.GARANT_BASE_URL} | "
        f"Log Level: {Config.LOG_LEVEL} | "
        f"BASE_DIR: {BASE_DIR} | "
        f".env: {BASE_DIR / '.env'} | "
        f"Token loaded: {bool(Config.GARANT_TOKEN)}"
    )

    # Run server with stdio transport (for opencode)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
