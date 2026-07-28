import time
from fastapi import FastAPI, Request, UploadFile, File, Form
from app.api.routes import router
from app.api.dependencies import create_db_and_tables
from contextlib import asynccontextmanager
from app.db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.core import setup_logging, get_logger
from app.agent import process_pdf_and_ask_question

#--app intialization--
app = FastAPI

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
origins = [
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8501",
    "http://localhost:8000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_bytes = await file.read()
    process_pdf_to_db(file_bytes)
    return {"status": "success"}


@app.post("/chat")
async def chat_with_agent(question: str = Form(...)):
    answer = ask_agent_question(question)
    return {"question": question, "answer": answer}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port=8000)