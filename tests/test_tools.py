"""Tests for MCP tools."""

import pytest
from pathlib import Path


@pytest.mark.asyncio
class TestTools:
    """Test MCP tools."""
    
    async def test_search_documents_tool(self):
        """Test search_documents tool."""
        from garant_mcp.tools import search_documents
        
        result = await search_documents("налог")
        
        assert isinstance(result, str)
        assert "documents" in result
    
    async def test_get_document_info_tool(self):
        """Test get_document_info tool."""
        from garant_mcp.tools import get_document_info
        
        result = await get_document_info(12138291)
        
        assert isinstance(result, str)
        assert "topic" in result
    
    async def test_create_legal_document_tool(self):
        """Test create_legal_document tool."""
        from garant_mcp.tools import create_legal_document
        
        text = "Статья 36 ЖК РФ"
        result = await create_legal_document(text)
        
        assert isinstance(result, str)
        assert "href" in result
    
    async def test_get_usage_limits_tool(self):
        """Test get_usage_limits tool."""
        from garant_mcp.tools import get_usage_limits
        
        result = await get_usage_limits()
        
        assert isinstance(result, str)
        assert "Постановка ссылки" in result or "error" in result
