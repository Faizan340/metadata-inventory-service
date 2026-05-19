from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    """Initialize the asynchronous MongoDB connection."""
    db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_instance.db = db_instance.client[settings.MONGO_DB_NAME]
    await db_instance.db.metadata.create_index("url", unique=True)
    print("Successfully connected to MongoDB.")

async def close_mongo_connection():
    """Close the MongoDB connection cleanly."""
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed.")
        
def get_db():
    """Utility to inject the database session into our FastAPI routes."""
    return db_instance.db
