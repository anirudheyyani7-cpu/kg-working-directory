from fastapi import APIRouter, Depends, Query
from app.database import get_driver
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
async def search(
    q: str = Query(..., min_length=1),
    labels: str = Query(None, description="Comma-separated labels: Company,Technology,..."),
    limit: int = Query(20, ge=1, le=100),
    driver=Depends(get_driver),
):
    label_list = [l.strip() for l in labels.split(",")] if labels else None
    return await search_service.search_entities(driver, q, label_list, limit)
