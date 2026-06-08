from fastapi import APIRouter, Depends, Query
from app.database import get_driver
from app.services import graph_service

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/competitors/{company_id}")
async def get_competitors(company_id: str, driver=Depends(get_driver)):
    return await graph_service.get_competitors(driver, company_id)


@router.get("/events")
async def get_events(
    type: str = Query(None, description="M&A, Partnership, Product Launch, etc."),
    since: str = Query(None, description="ISO date string, e.g. 2023-01-01"),
    driver=Depends(get_driver),
):
    return await graph_service.get_events(driver, type, since)
