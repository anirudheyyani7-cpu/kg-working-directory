from fastapi import APIRouter, Depends, BackgroundTasks
from app.database import get_driver
from app.models.relationships import ArticleIngestion
from app.services.extraction_service import extract_entities
from app.ingestion.mapper import map_to_graph
from app.ingestion.scheduler import get_state, trigger_ingestion
from app.ingestion.deduplicator import get_queue_depth

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/article")
async def ingest_article(article: ArticleIngestion, driver=Depends(get_driver)):
    extraction = await extract_entities(article.content, article.title, article.source)
    new_rels = await map_to_graph(extraction, article, driver)
    return {
        "entities_extracted": len(extraction.entities),
        "relationships_extracted": len(extraction.relationships),
        "new_relationships_written": new_rels,
        "entities": [{"type": e.type, "name": e.name, "confidence": e.confidence} for e in extraction.entities],
        "relationships": [
            {"source": r.source_name, "type": r.relationship_type, "target": r.target_name, "confidence": r.confidence}
            for r in extraction.relationships
        ],
    }


@router.post("/trigger")
async def trigger_ingest(background_tasks: BackgroundTasks, driver=Depends(get_driver)):
    background_tasks.add_task(trigger_ingestion, driver)
    return {"message": "Ingestion run triggered in background"}


@router.get("/status")
async def get_status():
    state = get_state()
    queue_depth = await get_queue_depth()
    return {**state, "queue_depth": queue_depth}
