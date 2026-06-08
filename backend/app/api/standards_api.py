from fastapi import APIRouter, Depends, Query
from app.database import get_driver
from app.services import graph_service

router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("/")
async def get_standards(
    body: str = Query(None, description="Issuing body e.g. 3GPP, ITU-R"),
    status: str = Query(None, description="Frozen, Stable, Draft"),
    driver=Depends(get_driver),
):
    return await graph_service.get_standards(driver, body, status)


@router.get("/{standard_id}/implementors")
async def get_implementors(standard_id: str, driver=Depends(get_driver)):
    return await graph_service.get_standard_implementors(driver, standard_id)
