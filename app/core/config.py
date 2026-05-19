from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HTTP Metadata Inventory Service"
    # Defaults to localhost for local testing, but Docker will override this
    MONGO_URI: str = "mongodb://localhost:27017" 
    MONGO_DB_NAME: str = "metadata_inventory"

    class Config:
        env_file = ".env"

settings = Settings()