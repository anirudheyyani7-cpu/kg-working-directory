import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_get_node_not_found(mock_driver):
    driver, session = mock_driver
    result = AsyncMock()
    result.single = AsyncMock(return_value=None)
    session.run = AsyncMock(return_value=result)

    from app.services.graph_service import get_node
    node = await get_node(driver, "nonexistent-id")
    assert node is None


@pytest.mark.asyncio
async def test_get_competitors_returns_list(mock_driver):
    driver, session = mock_driver
    mock_record = MagicMock()
    mock_record.data.return_value = {
        "name": "Nokia", "revenue": 22.3, "segment": "RAN Vendor",
        "country": "FI", "acquisitions": [], "products": ["Nokia AirScale"],
    }
    result = AsyncMock()
    result.__aiter__ = AsyncMock(return_value=iter([mock_record]))

    async def aiter_records():
        yield mock_record

    result.__aiter__ = lambda self: aiter_records()
    session.run = AsyncMock(return_value=result)

    from app.services.graph_service import get_competitors
    competitors = await get_competitors(driver, "Ericsson")
    assert isinstance(competitors, list)
