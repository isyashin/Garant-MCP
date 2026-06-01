"""Test configuration and fixtures."""

import pytest
import pytest_asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from garant_mcp.client import GarantClient
from garant_mcp.config import Config


@pytest.fixture
def token():
    """Get token from environment or skip tests."""
    token = Config.GARANT_TOKEN
    if not token:
        pytest.skip("GARANT_TOKEN not set")
    return token


@pytest_asyncio.fixture
async def client(token):
    """Create test client."""
    async with GarantClient(token=token) as client:
        yield client


@pytest.fixture
def sample_topic():
    """Sample document topic ID for testing."""
    return 12138291  # ЖК РФ


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return "налог"
