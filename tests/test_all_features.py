"""Comprehensive feature tests for Garant MCP Server.

This test suite uses:
- Real API calls for FREE endpoints (search, snippets, prime, sutyazhnik, limits)
- Mocked HTTP responses for PAID endpoints to avoid consuming API quotas
- Local filesystem tests for file_tools
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import pytest_asyncio
import respx
from httpx import Response

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from garant_mcp.client import GarantClient
from garant_mcp.config import Config
from garant_mcp import tools as mcp_tools
from garant_mcp import resources as mcp_resources
from garant_mcp.server import mcp as fastmcp_server
from garant_mcp.file_tools import (
    CASES_ROOT,
    copy_docx_to_case,
    copy_template,
    create_case_folder,
    create_log,
    list_documents,
    load_document,
    save_document,
    save_to_case,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear persistent disk cache before every test to avoid mock misses."""
    from garant_mcp.cache import GarantCache

    cache = GarantCache()
    cache.clear()
    cache.close()
    yield


@pytest_asyncio.fixture
async def client():
    """Create a real GarantClient instance."""
    async with GarantClient() as c:
        yield c


@pytest.fixture
def sample_topic():
    """Sample document topic for tests."""
    return 10900200  # НК РФ часть 1


@pytest.fixture
def sample_topic_name():
    return "Налоговый кодекс Российской Федерации. Часть первая"


@pytest.fixture
def search_query():
    return "налог"


# ---------------------------------------------------------------------------
# FREE endpoints - real API
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSearchFreeEndpoints:
    """Test free /search endpoint against real API."""

    async def test_search_documents_basic(self, client, search_query):
        result = await client.search_documents(text=search_query)

        assert "documents" in result
        assert "totalPages" in result
        assert isinstance(result["documents"], list)
        assert len(result["documents"]) > 0
        assert "topic" in result["documents"][0]
        assert "name" in result["documents"][0]

    async def test_search_with_query_language(self, client):
        result = await client.search_documents(
            text="Type(Закон) & MorphoText(налог)",
            is_query=True,
        )

        assert "documents" in result
        assert result["totalPages"] > 0

    async def test_search_arbitr_env(self, client):
        result = await client.search_documents(
            text="арбитраж",
            env="arbitr",
        )

        assert "documents" in result
        assert result["totalPages"] >= 0

    async def test_search_empty_result(self, client):
        result = await client.search_documents(
            text="xyznonexistent12345",
        )

        assert "documents" in result
        assert isinstance(result["documents"], list)


@pytest.mark.asyncio
class TestSnippetsFreeEndpoint:
    """Test free /snippets endpoint against real API."""

    async def test_get_snippets(self, client, sample_topic, search_query):
        result = await client.get_snippets(text=search_query, topic=sample_topic)

        assert "snippets" in result
        assert isinstance(result["snippets"], list)


@pytest.mark.asyncio
class TestPrimeFreeEndpoints:
    """Test free PRIME endpoints against real API."""

    async def test_get_prime_categories(self, client):
        result = await client.get_prime_categories()

        assert "categories" in result
        assert isinstance(result["categories"], list)
        assert len(result["categories"]) > 0

    async def test_get_prime_news(self, client):
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
class TestSutyazhnikFreeEndpoint:
    """Test free /sutyazhnik-search endpoint against real API."""

    async def test_search_judicial_practice(self, client):
        result = await client.search_judicial_practice(
            text="арбитражный управляющий",
            count=5,
            kind=["301", "302"],
        )

        assert "documents" in result
        assert isinstance(result["documents"], list)


@pytest.mark.asyncio
class TestLimitsFreeEndpoint:
    """Test free /limits endpoint against real API."""

    async def test_get_limits(self, client):
        result = await client.get_limits()

        assert isinstance(result, list)
        assert len(result) > 0
        assert "title" in result[0]
        assert "value" in result[0]
        assert "names" in result[0]


# ---------------------------------------------------------------------------
# PAID endpoints - mocked HTTP
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestDocumentInfoMocked:
    """Test paid /topic/{topic} endpoint with mocked responses."""

    async def test_get_document_info_success(self, sample_topic, sample_topic_name):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}").mock(
                return_value=Response(
                    200,
                    json={
                        "topic": sample_topic,
                        "name": sample_topic_name,
                        "status": "Действующие",
                        "access": "ACCESS_IS_FREE",
                        "last_modified": "2024-01-01",
                        "isFree": True,
                    },
                )
            )

            async with GarantClient() as client:
                result = await client.get_document_info(sample_topic)

        assert result["topic"] == sample_topic
        assert result["name"] == sample_topic_name
        assert result["status"] == "Действующие"

    async def test_get_document_info_not_found(self):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get("/topic/99999999").mock(
                return_value=Response(403, text="Forbidden or not found")
            )

            async with GarantClient() as client:
                result = await client.get_document_info(99999999)

        assert "error" in result
        assert result["status"] in (403, 404)


@pytest.mark.asyncio
class TestHyperlinksMocked:
    """Test paid /find-hyperlinks endpoint with mocked responses."""

    async def test_create_hyperlinks(self):
        input_text = "В соответствии со статьей 36 ЖК РФ"
        output_text = 'В соответствии со <a href="#/document/12138291/entry/36">статьей 36 ЖК РФ</a>'

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.post("/find-hyperlinks").mock(
                return_value=Response(200, json={"text": output_text})
            )

            async with GarantClient() as client:
                result = await client.create_hyperlinks(text=input_text)

        assert result["text"] == output_text


@pytest.mark.asyncio
class TestMonitoringMocked:
    """Test paid monitoring endpoints with mocked responses."""

    async def test_find_modified(self, sample_topic):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.post("/find-modified").mock(
                return_value=Response(
                    200,
                    json={
                        "topics": [
                            {
                                "topic": sample_topic,
                                "modStatus": 1,
                                "modDate": "2025-01-15",
                            }
                        ]
                    },
                )
            )

            async with GarantClient() as client:
                result = await client.find_modified(
                    topics=[sample_topic],
                    mod_date="2025-01-01",
                    need_events=True,
                )

        assert "topics" in result
        assert result["topics"][0]["modStatus"] == 1

    async def test_block_on_control_changed(self):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.post("/block-on-control/changed").mock(
                return_value=Response(
                    200,
                    json={"urls": [{"url": "#/doc/123/entry/36", "changed": True}]},
                )
            )

            async with GarantClient() as client:
                result = await client.block_on_control_changed(
                    from_date="2025-01-01",
                    url_array=["#/doc/123/entry/36"],
                    need_events=True,
                )

        assert "urls" in result


@pytest.mark.asyncio
class TestExportsMocked:
    """Test paid export endpoints with mocked binary responses."""

    async def test_export_document_rtf(self, sample_topic, tmp_path):
        fake_rtf = b"{\\rtf1\\ansi Test RTF content}"

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/download").mock(
                return_value=Response(
                    200, content=fake_rtf, headers={"content-type": "application/rtf"}
                )
            )

            async with GarantClient() as client:
                path = await client.export_document_rtf(sample_topic, tmp_path)

        assert path.exists()
        assert path.read_bytes() == fake_rtf
        assert path.suffix == ".rtf"

    async def test_export_document_pdf(self, sample_topic, tmp_path):
        fake_pdf = b"%PDF-1.4 fake pdf content"

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/download-pdf").mock(
                return_value=Response(
                    200, content=fake_pdf, headers={"content-type": "application/pdf"}
                )
            )

            async with GarantClient() as client:
                path = await client.export_document_pdf(sample_topic, tmp_path)

        assert path.exists()
        assert path.read_bytes() == fake_pdf
        assert path.suffix == ".pdf"

    async def test_export_document_odt(self, sample_topic, tmp_path):
        fake_odt = b"PK\x03\x04 fake odt content"

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/download-odt").mock(
                return_value=Response(
                    200,
                    content=fake_odt,
                    headers={"content-type": "application/vnd.oasis.opendocument.text"},
                )
            )

            async with GarantClient() as client:
                path = await client.export_document_odt(sample_topic, tmp_path)

        assert path.exists()
        assert path.read_bytes() == fake_odt
        assert path.suffix == ".odt"

    async def test_export_document_html(self, sample_topic):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/html").mock(
                return_value=Response(
                    200,
                    json={
                        "items": [
                            {"number": 1, "text": "<p>Page 1</p>"},
                            {"number": 2, "text": "<p>Page 2</p>"},
                        ]
                    },
                )
            )

            async with GarantClient() as client:
                result = await client.export_document_html(sample_topic)

        assert "items" in result
        assert len(result["items"]) == 2

    async def test_export_block_html(self, sample_topic):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/entry/36/html").mock(
                return_value=Response(
                    200,
                    json={
                        "entry": 36,
                        "title": "Статья 36",
                        "text": "<p>Текст статьи 36</p>",
                        "ancestors": [],
                        "respondents": [],
                    },
                )
            )

            async with GarantClient() as client:
                result = await client.export_block_html(sample_topic, 36)

        assert result["entry"] == 36
        assert "text" in result


@pytest.mark.asyncio
class TestImagesAndFormulasMocked:
    """Test paid image/formula endpoints with mocked binary responses."""

    async def test_get_image(self, tmp_path):
        fake_png = b"\x89PNG\r\n\x1a\n fake image"
        object_id = 12345

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/image/{object_id}").mock(
                return_value=Response(
                    200, content=fake_png, headers={"content-type": "image/png"}
                )
            )

            async with GarantClient() as client:
                path = await client.get_image(object_id, tmp_path)

        assert path.exists()
        assert path.read_bytes() == fake_png

    async def test_get_formula(self, tmp_path):
        fake_png = b"\x89PNG\r\n\x1a\n fake formula"
        text = "x^2 + y^2 = z^2"

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get("/formula").mock(
                return_value=Response(
                    200, content=fake_png, headers={"content-type": "image/png"}
                )
            )

            async with GarantClient() as client:
                path = await client.get_formula(text, tmp_path)

        assert path.exists()
        assert path.read_bytes() == fake_png


# ---------------------------------------------------------------------------
# MCP Tools layer
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestToolsRealLimits:
    """Test tool wrappers that call the working /limits endpoint."""

    async def test_get_usage_limits_tool(self):
        result = await mcp_tools.get_usage_limits()

        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, list)
        assert "title" in data[0]


@pytest.mark.asyncio
class TestToolsRealAPI:
    """Test tool wrappers that call free endpoints."""

    async def test_search_documents_tool(self, search_query):
        result = await mcp_tools.search_documents(search_query)

        assert isinstance(result, str)
        data = json.loads(result)
        assert "documents" in data

    async def test_get_prime_categories_tool(self):
        result = await mcp_tools.get_prime_categories()

        assert isinstance(result, str)
        data = json.loads(result)
        assert "categories" in data

    async def test_get_prime_news_tool(self):
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        result = await mcp_tools.get_prime_news(
            categories=[24],
            from_date=from_date,
            to_date=to_date,
        )

        assert isinstance(result, str)
        data = json.loads(result)
        assert "news" in data

    async def test_search_judicial_practice_tool(self):
        result = await mcp_tools.search_judicial_practice(
            text="арбитражный управляющий",
            count=5,
        )

        assert isinstance(result, str)
        data = json.loads(result)
        assert "documents" in data


@pytest.mark.asyncio
class TestToolsMocked:
    """Test tool wrappers for paid endpoints with mocked HTTP."""

    async def test_get_document_info_tool(self, sample_topic, sample_topic_name):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}").mock(
                return_value=Response(
                    200,
                    json={
                        "topic": sample_topic,
                        "name": sample_topic_name,
                        "status": "Действующие",
                    },
                )
            )

            result = await mcp_tools.get_document_info(sample_topic)

        assert isinstance(result, str)
        data = json.loads(result)
        assert data["topic"] == sample_topic

    async def test_create_legal_document_tool(self):
        input_text = "Статья 36 ЖК РФ"
        output_text = '<a href="#/document/12138291/entry/36">Статья 36 ЖК РФ</a>'

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.post("/find-hyperlinks").mock(
                return_value=Response(200, json={"text": output_text})
            )

            result = await mcp_tools.create_legal_document(input_text)

        assert isinstance(result, str)
        assert "href" in result

    async def test_export_document_pdf_tool(self, sample_topic, tmp_path):
        fake_pdf = b"%PDF-1.4 fake"

        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}/download-pdf").mock(
                return_value=Response(
                    200, content=fake_pdf, headers={"content-type": "application/pdf"}
                )
            )

            import garant_mcp.config as config_module

            original_export_dir = config_module.Config.EXPORT_DIR
            config_module.Config.EXPORT_DIR = str(tmp_path)

            try:
                result = await mcp_tools.export_document_pdf(sample_topic)
                assert isinstance(result, str)
                assert Path(result).exists()
                assert Path(result).read_bytes() == fake_pdf
            finally:
                config_module.Config.EXPORT_DIR = original_export_dir


# ---------------------------------------------------------------------------
# File tools
# ---------------------------------------------------------------------------


class TestFileTools:
    """Test local file management tools."""

    def test_create_case_folder(self, tmp_path):
        original_root = CASES_ROOT
        try:
            # Temporarily redirect cases root
            from garant_mcp import file_tools

            file_tools.CASES_ROOT = tmp_path / "кейсы"

            case_path = create_case_folder("Тест_кейса")
            path = Path(case_path)

            assert path.exists()
            assert (path / "исходные данные").exists()
            assert (path / "результат").exists()
            assert (path / "служебное для агента").exists()
        finally:
            file_tools.CASES_ROOT = original_root

    def test_save_to_case(self, tmp_path):
        original_root = CASES_ROOT
        try:
            from garant_mcp import file_tools

            file_tools.CASES_ROOT = tmp_path / "кейсы"

            case_path = create_case_folder("Тест_сохранения")

            fp1 = save_to_case("content1", case_path, "test1.txt", "исходные данные")
            fp2 = save_to_case("content2", case_path, "test2.txt", "результат")
            fp3 = save_to_case(
                "content3", case_path, "test3.txt", "служебное для агента"
            )

            assert Path(fp1).read_text(encoding="utf-8") == "content1"
            assert Path(fp2).read_text(encoding="utf-8") == "content2"
            assert Path(fp3).read_text(encoding="utf-8") == "content3"
        finally:
            file_tools.CASES_ROOT = original_root

    def test_save_load_list_document(self, tmp_path):
        # Use output category which writes to results/output; we can't easily redirect,
        # so just test that save returns a path and list includes it.
        content = "Test document content"
        filepath = save_document(content, "test_all_features_doc.txt", "output")

        assert Path(filepath).exists()

        loaded = load_document("test_all_features_doc.txt", "output")
        assert loaded == content

        docs = list_documents("output")
        assert "test_all_features_doc.txt" in docs

    def test_copy_template(self, tmp_path):
        template_dir = Path("results") / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        template_file = template_dir / "test_template_all.txt"
        template_file.write_text("Template content", encoding="utf-8")

        dest = tmp_path / "copied_template.txt"
        result = copy_template("test_template_all.txt", str(dest))

        assert Path(result).exists()
        assert Path(result).read_text(encoding="utf-8") == "Template content"

        template_file.unlink()

    def test_create_log(self, tmp_path):
        create_log("test_all_features_case", "Test action", "Test details")

        log_dir = Path("results") / "logs"
        log_file = log_dir / "log.txt"
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test action" in content

    def test_copy_docx_to_case(self, tmp_path):
        original_root = CASES_ROOT
        try:
            from garant_mcp import file_tools

            file_tools.CASES_ROOT = tmp_path / "кейсы"

            case_path = create_case_folder("Тест_docx")
            source = tmp_path / "source.docx"
            source.write_text("fake docx", encoding="utf-8")

            result = copy_docx_to_case(str(source), case_path, "result.docx")

            assert Path(result).exists()
            assert Path(result).name == "result.docx"
        finally:
            file_tools.CASES_ROOT = original_root


# ---------------------------------------------------------------------------
# MCP Resources
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestResourcesMocked:
    """Test MCP resources with mocked HTTP."""

    async def test_document_resource(self, sample_topic, sample_topic_name):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get(f"/topic/{sample_topic}").mock(
                return_value=Response(
                    200,
                    json={
                        "topic": sample_topic,
                        "name": sample_topic_name,
                        "status": "Действующие",
                    },
                )
            )

            result = await mcp_resources.get_document_resource(sample_topic)

        data = json.loads(result)
        assert data["topic"] == sample_topic

    async def test_limits_resource(self):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get("/limits").mock(
                return_value=Response(
                    200,
                    json=[
                        {"title": "Экспорт", "value": 0, "names": ["topic/download"]}
                    ],
                )
            )

            result = await mcp_resources.get_limits_resource()

        data = json.loads(result)
        assert isinstance(data, list)
        assert data[0]["title"] == "Экспорт"

    async def test_prime_categories_resource(self):
        with respx.mock(
            base_url=Config.GARANT_BASE_URL, assert_all_mocked=True
        ) as rsps:
            rsps.get("/prime").mock(
                return_value=Response(
                    200,
                    json={
                        "categories": [
                            {"text": "Федеральное законодательство", "id": 24}
                        ]
                    },
                )
            )

            result = await mcp_resources.get_prime_categories_resource()

        data = json.loads(result)
        assert "categories" in data


# ---------------------------------------------------------------------------
# Server registration smoke tests
# ---------------------------------------------------------------------------


class TestServerRegistration:
    """Smoke tests that MCP server registered tools/resources/prompts."""

    def test_server_has_tools(self):
        tools = fastmcp_server._tool_manager._tools
        assert "search_documents_tool" in tools
        assert "get_document_info_tool" in tools
        assert "create_legal_document_tool" in tools
        assert "export_document_pdf_tool" in tools
        assert "save_text_document_tool" in tools
        assert "create_case_tool" in tools

    def test_server_has_resources(self):
        resources = fastmcp_server._resource_manager._resources
        templates = fastmcp_server._resource_manager._templates
        resource_uris = [str(r) for r in resources]
        template_uris = list(templates.keys())
        assert "garant://document/{topic}" in template_uris
        assert "garant://limits" in resource_uris
        assert "garant://prime/categories" in resource_uris

    def test_server_has_prompts(self):
        prompts = fastmcp_server._prompt_manager._prompts
        assert "legal_complaint" in prompts
        assert "contract_review" in prompts
        assert "document_analysis" in prompts
