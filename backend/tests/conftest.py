import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_driver():
    driver = MagicMock()
    session = AsyncMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=None)
    return driver, session
