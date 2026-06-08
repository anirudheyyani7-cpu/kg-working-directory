import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import get_driver, close_driver, setup_schema
from app.api.router import router
from app.ingestion.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TMT Knowledge Graph API...")
    driver = await get_driver()
    await setup_schema()
    start_scheduler(driver)
    yield
    stop_scheduler()
    await close_driver()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="TMT Knowledge Graph API",
    description="API for the Telecom, Media & Technology domain knowledge graph",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
