"""Simple in-memory cache as fallback when diskcache is not available."""

import time
import json
import hashlib
from typing import Any, Optional
from pathlib import Path


from .config import BASE_DIR


class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache: dict[str, tuple[Any, float]] = {}
        self.cache_dir = cache_dir or str(BASE_DIR / ".cache")
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _make_key(self, endpoint: str, params: dict) -> str:
        """Create cache key from endpoint and parameters."""
        key_data = f"{endpoint}:{json.dumps(params, sort_keys=True, default=str)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, endpoint: str, params: dict) -> Optional[Any]:
        """Get cached response."""
        key = self._make_key(endpoint, params)
        if key in self.cache:
            value, expires = self.cache[key]
            if time.time() < expires:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, endpoint: str, params: dict, value: Any, ttl: int) -> None:
        """Cache response with TTL."""
        key = self._make_key(endpoint, params)
        self.cache[key] = (value, time.time() + ttl)

    def delete(self, endpoint: str, params: dict) -> None:
        """Delete cached response."""
        key = self._make_key(endpoint, params)
        self.cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()

    def close(self) -> None:
        """Close cache."""
        self.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Try to import diskcache, fallback to simple cache
try:
    from diskcache import Cache  # type: ignore[import-untyped]

    class _GarantCache:
        """Cache manager using diskcache."""

        def __init__(self, cache_dir: Optional[str] = None):
            self.cache_dir = cache_dir or str(BASE_DIR / ".cache")
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
            self.cache = Cache(self.cache_dir)

        def _make_key(self, endpoint: str, params: dict) -> str:
            key_data = f"{endpoint}:{json.dumps(params, sort_keys=True, default=str)}"
            return hashlib.md5(key_data.encode()).hexdigest()

        def get(self, endpoint: str, params: dict) -> Optional[Any]:
            key = self._make_key(endpoint, params)
            return self.cache.get(key)

        def set(self, endpoint: str, params: dict, value: Any, ttl: int) -> None:
            key = self._make_key(endpoint, params)
            self.cache.set(key, value, expire=ttl)

        def delete(self, endpoint: str, params: dict) -> None:
            key = self._make_key(endpoint, params)
            self.cache.delete(key)

        def clear(self) -> None:
            self.cache.clear()

        def close(self) -> None:
            self.cache.close()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

    GarantCache = _GarantCache

except ImportError:
    # Fallback to simple cache
    class GarantCache(SimpleCache):  # type: ignore[no-redef]
        """Fallback cache manager using simple in-memory cache."""

        pass
