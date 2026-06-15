"""Tests for Garant API client."""

import pytest
from httpx import HTTPStatusError


@pytest.mark.asyncio
class TestSearch:
    """Test search functionality."""

    async def test_search_documents_basic(self, client, sample_search_query):
        """Test basic search."""
        result = await client.search_documents(text=sample_search_query)

        assert "documents" in result
        assert "totalPages" in result
        assert isinstance(result["documents"], list)
        assert len(result["documents"]) > 0

    async def test_search_with_query_language(self, client):
        """Test search with query language."""
        result = await client.search_documents(
            text="Type(Закон) & MorphoText(налог)",
            is_query=True,
        )

        assert "documents" in result
        assert result["totalPages"] > 0

    async def test_search_arbitr_env(self, client):
        """Test search in arbitr environment."""
        result = await client.search_documents(
            text="налог",
            env="arbitr",
        )

        assert "documents" in result
        assert result["totalPages"] > 0

    async def test_search_empty_result(self, client):
        """Test search with empty result."""
        result = await client.search_documents(
            text="xyznonexistent12345",
        )

        assert "documents" in result


@pytest.mark.asyncio
class TestDocumentInfo:
    """Test document information retrieval."""

    async def test_get_document_info_success(self, client, sample_topic):
        """Test getting document info."""
        result = await client.get_document_info(sample_topic)

        assert "topic" in result
        assert result["topic"] == sample_topic
        assert "name" in result
        assert "status" in result
        assert result["status"] == "Действующие"

    async def test_get_document_info_not_found(self, client):
        """Test getting non-existent document."""
        result = await client.get_document_info(99999999)

        assert "error" in result
        assert result["status"] == 403 or result["status"] == 404

    async def test_get_document_info_invalid_id(self, client):
        """Test getting document with invalid ID."""
        result = await client.get_document_info(0)

        assert "error" in result


@pytest.mark.asyncio
class TestExports:
    """Test export functionality."""

    async def test_export_document_html(self, client, sample_topic):
        """Test HTML export."""
        try:
            result = await client.export_document_html(sample_topic)
            assert "items" in result
            assert isinstance(result["items"], list)
            assert len(result["items"]) > 0
        except HTTPStatusError as e:
            if e.response.status_code == 423:
                pytest.skip("Document locked (423) - constitutional document")
            raise

    async def test_export_block_html(self, client, sample_topic):
        """Test block HTML export."""
        try:
            result = await client.export_block_html(sample_topic, 36)
            assert "entry" in result
            assert "text" in result
            assert result["entry"] == 36
        except HTTPStatusError as e:
            if e.response.status_code == 423:
                pytest.skip("Document locked (423) - constitutional document")
            raise

    async def test_export_document_rtf(self, client, sample_topic, tmp_path):
        """Test RTF export."""
        try:
            path = await client.export_document_rtf(sample_topic, tmp_path)
            assert path.exists()
            assert path.suffix == ".rtf"
            assert path.stat().st_size > 0
        except HTTPStatusError as e:
            if e.response.status_code == 423:
                pytest.skip("Document locked (423) - constitutional document")
            raise

    async def test_export_document_pdf(self, client, sample_topic, tmp_path):
        """Test PDF export."""
        try:
            path = await client.export_document_pdf(sample_topic, tmp_path)
            assert path.exists()
            assert path.suffix == ".pdf"
            assert path.stat().st_size > 0
        except HTTPStatusError as e:
            if e.response.status_code == 423:
                pytest.skip("Document locked (423) - constitutional document")
            raise


@pytest.mark.asyncio
class TestMonitoring:
    """Test monitoring functionality."""

    async def test_find_modified(self, client, sample_topic):
        """Test document modification check."""
        result = await client.find_modified(
            topics=[sample_topic],
            mod_date="2025-01-01",
            need_events=True,
        )

        assert "topics" in result
        if result["topics"]:
            assert "modStatus" in result["topics"][0]

    async def test_find_modified_too_many(self, client):
        """Test with too many documents."""
        result = await client.find_modified(
            topics=list(range(1000, 1101)),
            mod_date="2025-01-01",
        )

        assert "error" in result
        assert result["status"] == 400


@pytest.mark.asyncio
class TestPRIME:
    """Test PRIME functionality."""

    async def test_get_prime_categories(self, client):
        """Test getting PRIME categories."""
        result = await client.get_prime_categories()

        assert "categories" in result
        assert isinstance(result["categories"], list)
        assert len(result["categories"]) > 0

    async def test_get_prime_news(self, client):
        """Test getting PRIME news."""
        from datetime import datetime, timedelta

        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        result = await client.get_prime_news(
            categories=[24],
            from_date=from_date,
            to_date=to_date,
        )

        assert "news" in result
        assert isinstance(result["news"], list)


@pytest.mark.asyncio
class TestSutyazhnik:
    """Test Sutyazhnik functionality."""

    async def test_search_judicial_practice(self, client):
        """Test judicial practice search."""
        result = await client.search_judicial_practice(
            text="арбитражный управляющий",
            count=5,
            kind=["301", "302"],
        )

        assert "documents" in result
        assert isinstance(result["documents"], list)


@pytest.mark.asyncio
class TestLimits:
    """Test limits functionality."""

    async def test_get_limits(self, client):
        """Test getting usage limits."""
        result = await client.get_limits()

        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "value" in result[0]
