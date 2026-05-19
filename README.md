# HTTP Metadata Inventory Service

A robust, asynchronous FastAPI microservice containerized with Docker to fetch, index, and inventory static webpage metadata (headers, cookies, and source code) inside MongoDB.

## Architecture & Design Decisions
- **Internal Orchestration:** Utilizes FastAPI's native `BackgroundTasks` to handle cache-miss collections. This satisfies the requirement for internal orchestration without the overhead of external message brokers (like Celery/Redis).
- **Resilience:** External HTTP calls via `httpx` are strictly capped with a 10-second timeout to prevent dead URLs from hanging the background worker thread.
- **Performance:** A unique index is automatically built on the MongoDB `url` field at application startup to guarantee fast `O(1)` retrieval times as the dataset scales.
- **Validation:** Pydantic's `HttpUrl` model is enforced at the transport layer to automatically reject malformed payloads.

## Running the Application
Ensure Docker is running on your host machine. This command will spin up both the FastAPI application and the MongoDB database.

    docker-compose up --build

### Interacting with the API
Once the containers are running, navigate to the auto-generated Swagger UI to test the endpoints:
- **API Documentation (Swagger UI):** http://localhost:8000/docs
- **System Health Check:** http://localhost:8000/health

## Executing the Test Suite
The test suite utilizes `pytest` and `pytest-asyncio` to execute integration tests. It actively mocks the network I/O and database layers to evaluate system logic in isolation.

To run the tests locally:

    pip install -r requirements.txt
    pytest -v
