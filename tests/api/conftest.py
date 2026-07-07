from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


class FakeAsyncCM:
    """Stand-in for AsyncSession / session.begin() async context managers."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        pass

    async def __aenter__(self) -> "FakeAsyncCM":
        return self

    async def __aexit__(self, *args) -> None:  # noqa: ANN002
        return None

    def begin(self) -> "FakeAsyncCM":
        return FakeAsyncCM()


@pytest.fixture
def app():  # noqa: ANN201
    from backend.api import app as fastapi_app

    fastapi_app.dependency_overrides.clear()
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client(app):  # noqa: ANN001, ANN201
    """TestClient with the DB lifespan hooks stubbed out (no real engine)."""
    from backend.api import dependencies as deps

    with (
        patch.object(deps.async_db_manager, "initialize"),
        patch.object(deps.async_db_manager, "close", new=AsyncMock()),
        patch.object(deps.process_manager, "close"),
    ):
        with TestClient(app) as test_client:
            yield test_client
