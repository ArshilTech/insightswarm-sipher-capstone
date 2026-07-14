import time
from fastapi import FastAPI, Request
from app.api.routes import router
from app.api.dependencies import create_db_and_tables
from contextlib import asynccontextmanager
from app.db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.core import setup_logging, get_logger

# Setup logging before app creation
setup_logging()
logger = get_logger(__name__)

# Define the lifespan context manager to create the database and tables on startup
@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("Initializing database and tables on startup...")
    await create_db_and_tables()
    yield 
    logger.info("Disposing of database engine on shutdown...")
    await engine.dispose()  # Dispose of the engine on shutdown

app = FastAPI(title="LangGraph Research API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP middleware for request logging
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
    )
    return response

app.include_router(router, prefix="/api", tags=["API"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

