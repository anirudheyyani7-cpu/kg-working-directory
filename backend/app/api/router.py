from fastapi import APIRouter
from app.api import graph, search, taxonomy, intelligence, ingest, standards_api

router = APIRouter(prefix="/api")
router.include_router(graph.router)
router.include_router(search.router)
router.include_router(taxonomy.router)
router.include_router(intelligence.router)
router.include_router(ingest.router)
router.include_router(standards_api.router)
