"""HTTP client for Garant API."""

import httpx
import base64
import logging
from typing import Any, Optional
from pathlib import Path
from .config import Config
from .cache import GarantCache

logger = logging.getLogger(__name__)


class GarantClient:
    """Client for Garant API."""
    
    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or Config.GARANT_TOKEN
        self.base_url = base_url or Config.GARANT_BASE_URL
        self.cache = GarantCache()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """Make HTTP request with caching and error handling."""
        cache_key = endpoint.replace("/", "_")
        
        # Try cache for GET requests
        if method == "GET" and use_cache:
            cached = self.cache.get(cache_key, params or {})
            if cached is not None:
                logger.debug(f"Cache hit for {endpoint}")
                return cached
        
        try:
            if method == "GET":
                response = await self.client.get(endpoint, params=params)
            elif method == "POST":
                response = await self.client.post(endpoint, json=json_data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Handle errors
            if response.status_code == 503:
                logger.error(f"Authentication error (503) for {endpoint}")
                raise Exception("Authentication error: Invalid token (503)")
            elif response.status_code == 401:
                logger.error(f"Unauthorized (401) for {endpoint}")
                raise Exception("Unauthorized: Check your token")
            elif response.status_code == 404:
                logger.warning(f"Not found (404) for {endpoint}")
                return {"error": "Not found", "status": 404}
            elif response.status_code == 403:
                logger.warning(f"Forbidden (403) for {endpoint}")
                return {"error": "Forbidden or not found", "status": 403}
            elif response.status_code == 400:
                logger.warning(f"Bad request (400) for {endpoint}: {response.text[:200]}")
                return {"error": "Bad request", "status": 400, "details": response.text[:200]}
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429) for {endpoint}")
                raise Exception("Rate limited: Too many requests")
            
            response.raise_for_status()
            
            # Parse JSON response
            try:
                data = response.json()
            except Exception:
                data = {"content": response.text, "content_type": response.headers.get("content-type")}
            
            # Cache successful GET responses
            if method == "GET" and use_cache:
                ttl = self.cache.get_ttl(cache_key) if hasattr(self.cache, 'get_ttl') else 300
                self.cache.set(cache_key, params or {}, data, ttl)
                logger.debug(f"Cache set for {endpoint}")
            
            return data
            
        except httpx.RequestError as e:
            logger.error(f"Request error for {endpoint}: {str(e)}")
            raise Exception(f"Request error: {str(e)}")
    
    async def _download(
        self,
        endpoint: str,
        output_path: Path,
        params: Optional[dict] = None,
    ) -> Path:
        """Download binary file."""
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"File downloaded: {output_path} ({len(response.content)} bytes)")
            return output_path
            
        except httpx.RequestError as e:
            logger.error(f"Download error for {endpoint}: {str(e)}")
            raise Exception(f"Download error: {str(e)}")
    
    # === Search ===
    
    async def search_documents(
        self,
        text: str,
        env: str = "internet",
        sort: int = 0,
        sort_order: int = 0,
        page: int = 1,
        is_query: bool = False,
    ) -> dict[str, Any]:
        """Search documents."""
        data = {
            "text": text,
            "env": env,
            "sort": sort,
            "sortOrder": sort_order,
            "page": page,
        }
        if is_query:
            data["isQuery"] = True
        return await self._request("POST", "/search", json_data=data, use_cache=False)
    
    # === Document Info ===
    
    async def get_document_info(self, topic: int) -> dict[str, Any]:
        """Get document information."""
        return await self._request("GET", f"/topic/{topic}")
    
    # === Snippets ===
    
    async def get_snippets(
        self,
        text: str,
        topic: int,
        correspondent: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Get text snippets."""
        data = {"text": text, "topic": topic}
        if correspondent:
            data["correspondent"] = correspondent
        return await self._request("POST", "/snippets", json_data=data)
    
    # === Hyperlinks ===
    
    async def create_hyperlinks(self, text: str, base_url: str = "https://internet.garant.ru") -> dict[str, Any]:
        """Create hyperlinks in text."""
        data = {"text": text, "baseUrl": base_url}
        return await self._request("POST", "/find-hyperlinks", json_data=data, use_cache=False)
    
    # === Monitoring ===
    
    async def find_modified(
        self,
        topics: list[int],
        mod_date: str,
        need_events: bool = False,
    ) -> dict[str, Any]:
        """Check document modifications."""
        data = {
            "topics": topics,
            "modDate": mod_date,
            "needEvents": need_events,
        }
        return await self._request("POST", "/find-modified", json_data=data, use_cache=False)
    
    async def block_on_control_changed(
        self,
        from_date: str,
        url_array: list[str],
        need_events: bool = False,
    ) -> dict[str, Any]:
        """Check block modifications."""
        data = {
            "fromDate": from_date,
            "urlArray": url_array,
            "needEvents": need_events,
        }
        return await self._request("POST", "/block-on-control/changed", json_data=data, use_cache=False)
    
    # === Exports ===
    
    async def export_document_rtf(self, topic: int, output_dir: Optional[Path] = None) -> Path:
        """Export document to RTF."""
        output_path = (output_dir or Path(Config.EXPORT_DIR)) / f"{topic}.rtf"
        return await self._download(f"/topic/{topic}/download", output_path)
    
    async def export_document_html(self, topic: int) -> dict[str, Any]:
        """Export document to HTML."""
        return await self._request("GET", f"/topic/{topic}/html")
    
    async def export_block_html(self, topic: int, entry: int) -> dict[str, Any]:
        """Export block to HTML."""
        return await self._request("GET", f"/topic/{topic}/entry/{entry}/html")
    
    async def export_document_odt(self, topic: int, output_dir: Optional[Path] = None) -> Path:
        """Export document to ODT."""
        output_path = (output_dir or Path(Config.EXPORT_DIR)) / f"{topic}.odt"
        return await self._download(f"/topic/{topic}/download-odt", output_path)
    
    async def export_document_pdf(self, topic: int, output_dir: Optional[Path] = None) -> Path:
        """Export document to PDF."""
        output_path = (output_dir or Path(Config.EXPORT_DIR)) / f"{topic}.pdf"
        return await self._download(f"/topic/{topic}/download-pdf", output_path)
    
    # === Images and Formulas ===
    
    async def get_image(self, object_id: int, output_dir: Optional[Path] = None) -> Path:
        """Get image by object_id."""
        output_path = (output_dir or Path(Config.EXPORT_DIR)) / f"image_{object_id}.png"
        return await self._download(f"/image/{object_id}", output_path)
    
    async def get_formula(self, text: str, output_dir: Optional[Path] = None) -> Path:
        """Get formula as image."""
        encoded_text = base64.b64encode(text.encode()).decode()
        output_path = (output_dir or Path(Config.EXPORT_DIR)) / f"formula_{encoded_text[:20]}.png"
        return await self._download("/formula", output_path, params={"text": encoded_text, "fmt": "png"})
    
    # === PRIME ===
    
    async def get_prime_categories(self) -> dict[str, Any]:
        """Get PRIME categories."""
        return await self._request("GET", "/prime")
    
    async def get_prime_news(
        self,
        categories: list[int],
        from_date: str,
        to_date: str,
        sort: int = 1,
    ) -> dict[str, Any]:
        """Get PRIME news feed."""
        data = {
            "categories": categories,
            "fromDate": from_date,
            "toDate": to_date,
            "sort": sort,
        }
        return await self._request("POST", "/prime/create-news", json_data=data)
    
    # === Sutyazhnik ===
    
    async def search_judicial_practice(
        self,
        text: str,
        count: int = 10,
        kind: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Search judicial practice."""
        data = {"text": text, "count": count}
        if kind:
            data["kind"] = kind
        return await self._request("POST", "/sutyazhnik-search", json_data=data)
    
    # === Limits ===
    
    async def get_limits(self) -> dict[str, Any]:
        """Get usage limits."""
        return await self._request("GET", "/limits")
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
        self.cache.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
