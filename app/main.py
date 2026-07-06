from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.db import init_pool, close_pool
from app.modules.documents.router import router as documents_router
from app.modules.extraction.router import router as extraction_router
from app.modules.comparison.router import router as comparison_router
from app.modules.jobs.router import router as jobs_router
from app.modules.health.router import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()

app = FastAPI(title="pbg-backend", lifespan=lifespan)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(extraction_router, prefix="/extraction", tags=["extraction"])
app.include_router(comparison_router, prefix="/comparison", tags=["comparison"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])