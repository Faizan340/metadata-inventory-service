import httpx
from datetime import datetime, timezone
from app.services.database import get_db
from app.models.schemas import MetadataRecord

async def fetch_url_metadata(url: str) -> dict:
    """Fetches headers, cookies, and page source from a given URL."""
    try:
        # 10-second timeout to ensure system resilience 
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            return {
                "url": url,
                "headers": dict(response.headers),
                "cookies": dict(response.cookies),
                "page_source": response.text
            }
    except httpx.RequestError as e:
        raise ValueError(f"Network error while fetching {url}: {str(e)}")

async def save_metadata(metadata: dict) -> MetadataRecord:
    """Validates and saves the scraped metadata into MongoDB."""
    db = get_db()
    record = MetadataRecord(**metadata)
    
    # We use an upsert to avoid duplicate entries for the same URL
    await db.metadata.update_one(
        {"url": record.url},
        {"$set": record.model_dump()},
        upsert=True
    )
    return record

async def background_scrape_task(url: str):
    """
    Internal background worker logic.
    Executes independently of the request-response cycle.
    """
    try:
        print(f"Starting background collection for {url}...")
        raw_metadata = await fetch_url_metadata(url)
        await save_metadata(raw_metadata)
        print(f"Background collection successfully completed for {url}.")
    except Exception as e:
        print(f"Background collection failed for {url}: {e}")