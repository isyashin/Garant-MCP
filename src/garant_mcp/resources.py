"""MCP Resources for Garant API."""

from .client import GarantClient
import json

client = GarantClient()


async def get_document_resource(topic: int) -> str:
    """
    Resource: garant://document/{topic}
    
    Returns document metadata including status, type, dates, and access info.
    """
    try:
        result = await client.get_document_info(topic)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_limits_resource() -> str:
    """
    Resource: garant://limits
    
    Returns current API usage limits and remaining quotas.
    """
    try:
        result = await client.get_limits()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


async def get_prime_categories_resource() -> str:
    """
    Resource: garant://prime/categories
    
    Returns PRIME news categories tree.
    """
    try:
        result = await client.get_prime_categories()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
