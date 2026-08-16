from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

import backend.api.dependencies as deps
from backend.application.services.api.nearby_stop_loader import NearbyStopLoaderService
from backend.application.services.api.route_loader import RouteLoaderService
from backend.application.services.api.stop_loader import StopLoaderService
from backend.application.services.api.trip_loader import TripLoaderService
from backend.domain.admin.session import AdminSession
from backend.domain.gtfs_rt.enums import City

from .conftest import FakeAsyncCM


def test_gtfs_engine_for_applies_schema(monkeypatch):
    engine = MagicMock()
    monkeypatch.setattr(deps.async_db_manager, "_async_engine", engine, raising=False)

    result = deps.gtfs_engine_for(City.MONTPELLIER)

    engine.execution_options.assert_called_once_with(
        schema_translate_map={"gtfs": City.MONTPELLIER}
    )
    assert result is engine.execution_options.return_value


async def test_get_gtfs_session_yields_session(monkeypatch):
    monkeypatch.setattr(deps, "gtfs_engine_for", lambda city: MagicMock())
    monkeypatch.setattr(deps, "AsyncSession", FakeAsyncCM)

    gen = deps.get_gtfs_session(City.MONTPELLIER)
    session = await gen.__anext__()
    assert isinstance(session, FakeAsyncCM)
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()


def test_loaders_are_wired():
    session = MagicMock()
    assert isinstance(deps.get_route_loader(session), RouteLoaderService)
    assert isinstance(deps.get_stop_loader(session), StopLoaderService)
    assert isinstance(deps.get_trip_loader(session), TripLoaderService)
    assert isinstance(deps.get_nearby_stop_loader(session), NearbyStopLoaderService)


async def test_require_admin_session_missing_token_raises():
    request = MagicMock()
    request.cookies = {}
    with pytest.raises(HTTPException) as exc_info:
        await deps.require_admin_session(request)
    assert exc_info.value.status_code == 401


async def test_require_admin_session_valid_token():
    request = MagicMock()
    request.cookies = {"admin_session": "tok"}
    session = AdminSession(email="a@b.c", expires_at=datetime.now(timezone.utc))
    with patch.object(deps.session_manager, "decode", return_value=session):
        result = await deps.require_admin_session(request)
    assert result.email == "a@b.c"


async def test_require_admin_session_invalid_token():
    request = MagicMock()
    request.cookies = {"admin_session": "bad"}

    def boom(_token):  # noqa: ANN001, ANN202
        raise ValueError("Invalid session")

    with patch.object(deps.session_manager, "decode", side_effect=boom):
        with pytest.raises(HTTPException) as exc_info:
            await deps.require_admin_session(request)
    assert exc_info.value.status_code == 401
