from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

import voice as twilio_router
import calls
from config import settings
from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Receptionist AI backend...")
    logger.info(f"Ollama URL: {settings.OLLAMA_URL}")
    logger.info(f"LLM Model: {settings.LLM_MODEL}")
    await init_db()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Receptionist AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(twilio_router.router, prefix="/twilio", tags=["twilio"])
app.include_router(calls.router, prefix="/calls", tags=["calls"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}