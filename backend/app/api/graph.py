from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_driver
from app.services import graph_service

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/node/{node_id}")
async def get_node(node_id: str, driver=Depends(get_driver)):
    node = await graph_service.get_node(driver, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.get("/neighbors/{node_id}")
async def get_neighbors(
    node_id: str,
    depth: int = Query(1, ge=1, le=3),
    types: str = Query(None, description="Comma-separated node types to filter"),
    driver=Depends(get_driver),
):
    node_types = [t.strip() for t in types.split(",")] if types else None
    return await graph_service.get_neighbors(driver, node_id, depth, node_types)


@router.get("/path")
async def get_path(
    from_id: str = Query(...),
    to_id: str = Query(...),
    driver=Depends(get_driver),
):
    return await graph_service.get_shortest_path(driver, from_id, to_id)


@router.get("/subgraph")
async def get_subgraph(
    label: str = Query("Company"),
    limit: int = Query(50, ge=1, le=200),
    driver=Depends(get_driver),
):
    return await graph_service.get_subgraph_by_label(driver, label, limit)
