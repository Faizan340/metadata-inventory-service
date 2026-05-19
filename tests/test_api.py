import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_db():
    """Fixture to mock MongoDB collection operations."""
    with patch("app.api.routes.get_db") as mock_get_db:
        mock_collection = AsyncMock()
        mock_db_instance = AsyncMock()
        mock_db_instance.metadata = mock_collection
        mock_get_db.return_value = mock_db_instance
        yield mock_collection

@pytest.fixture
def mock_scraper():
    """Fixture to mock the external HTTP utility."""
    with patch("app.api.routes.fetch_url_metadata") as mock_fetch:
        yield mock_fetch

# --- 1. Test POST Endpoint ---

@patch("app.api.routes.save_metadata")
def test_create_metadata_success(mock_save, mock_scraper):
    """Test successful POST scrape and save loop."""
    fake_payload = {
        "url": "https://example.com",
        "headers": {"content-type": "text/html"},
        "cookies": {},
        "page_source": "<html>Hello</html>"
    }
    mock_scraper.return_value = fake_payload
    mock_save.return_value = fake_payload

    response = client.post("/api/v1/metadata/", json={"url": "https://example.com"})
    
    assert response.status_code == 201
    assert response.json()["url"] == "https://example.com"
    mock_scraper.assert_called_once_with("https://example.com/")

def test_create_metadata_invalid_url():
    """Test validation failure for malformed URLs."""
    response = client.post("/api/v1/metadata/", json={"url": "not-a-valid-url"})
    assert response.status_code == 422  # FastAPI unprocessable entity

# --- 2. Test GET Endpoint (Cache Hit vs Cache Miss) ---

@pytest.mark.asyncio
async def test_get_metadata_cache_hit(mock_db):
    """Test immediate data return when URL exists in DB."""
    fake_doc = {
        "url": "https://example.com",
        "headers": {"server": "nginx"},
        "cookies": {},
        "page_source": "Cached Content"
    }
    # Simulate database inventory find success
    mock_db.find_one.return_value = fake_doc

    response = client.get("/api/v1/metadata/?url=https://example.com")
    
    assert response.status_code == 200
    assert response.json()["page_source"] == "Cached Content"
    mock_db.find_one.assert_called_once_with({"url": "https://example.com/"})

@pytest.mark.asyncio
async def test_get_metadata_cache_miss(mock_db):
    """Test instant 202 response and task registration on cache miss."""
    # Simulate missing database record
    mock_db.find_one.return_value = None

    response = client.get("/api/v1/metadata/?url=https://new-url.com")
    
    assert response.status_code == 202
    assert "process initiated" in response.json()["message"]