"""MCP Tools for Garant API."""

import json
import logging
from pathlib import Path
from typing import Optional
from .client import GarantClient
from .config import Config

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
