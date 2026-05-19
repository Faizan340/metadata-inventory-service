from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any
from datetime import datetime, timezone

class URLRequest(BaseModel):
    """Schema for the incoming POST request to scrape a URL."""
    url: HttpUrl = Field(..., description="The fully qualified URL to fetch metadata from")

class MetadataRecord(BaseModel):
    """Schema for the data stored in MongoDB and returned via GET."""
    url: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    page_source: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))