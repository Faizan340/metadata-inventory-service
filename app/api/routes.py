from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl

from app.models.schemas import URLRequest, MetadataRecord
from app.services.scraper import fetch_url_metadata, save_metadata, background_scrape_task
from app.services.database import get_db

router = APIRouter()

@router.post("/", response_model=MetadataRecord, status_code=status.HTTP_201_CREATED)
async def create_metadata(request: URLRequest):
    """POST Endpoint: Force a metadata scrape and store the results."""
    url_str = str(request.url)
    try:
        raw_data = await fetch_url_metadata(url_str)
        record = await save_metadata(raw_data)
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", status_code=status.HTTP_200_OK)
async def get_metadata(url: HttpUrl, background_tasks: BackgroundTasks):
    """
    GET Endpoint: Retrieve metadata. 
    If missing, returns 202 and triggers a background collection.
    """
    db = get_db()
    url_str = str(url)
    
    # Step 1: Inventory Check
    document = await db.metadata.find_one({"url": url_str})
    
    # Step 2: Immediate Resolution (Cache Hit)
    if document:
        return MetadataRecord(**document)
    
    # Step 3: Conditional Inventory Update (Cache Miss)
    # Add the scraping task to internal orchestration
    background_tasks.add_task(background_scrape_task, url_str)
    
    # Return immediate acknowledgement
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "message": "Metadata not found. Collection process initiated in the background.",
            "url": url_str
        }
    )