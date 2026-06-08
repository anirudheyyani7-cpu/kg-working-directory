from fastapi import APIRouter, Depends
from app.database import get_driver
from app.services import graph_service

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("/")
async def get_taxonomy(driver=Depends(get_driver)):
    return await graph_service.get_taxonomy(driver)
