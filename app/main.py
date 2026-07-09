from fastapi import FastAPI
from app.api.routes import router
from app.api.dependencies import create_db_and_tables
from contextlib import asynccontextmanager
from app.db.database import engine

# Define the lifespan context manager to create the database and tables on startup
@asynccontextmanager
async def lifespan(app : FastAPI):
    await create_db_and_tables()
    yield 
    await engine.dispose()  # Dispose of the engine on shutdown

app = FastAPI(title="LangGraph Research API", lifespan=lifespan)

app.include_router(router, prefix="/api", tags=["API"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

