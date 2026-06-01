"""Garant MCP Server - Main entry point."""

import sys
import json
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .config import Config
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
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr),
    ],
)

logger = logging.getLogger(__name__)

# Create logs directory
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Add file handler
file_handler = logging.FileHandler(log_dir / "garant-mcp.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

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
async def create_legal_document_tool(text: str, base_url: str = "https://internet.garant.ru") -> str:
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
    kind: list[str] = None,
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
        f"Log Level: {Config.LOG_LEVEL}"
    )
    
    # Run server with stdio transport (for opencode)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
