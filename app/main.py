from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.services.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await connect_to_mongo()
    yield
    # Shutdown logic
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A service to asynchronously inventory HTTP metadata.",
    version="1.0.0",
    lifespan=lifespan
)

# Register our API routes
app.include_router(api_router, prefix="/api/v1/metadata", tags=["Metadata Inventory"])

@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint for container orchestration."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}