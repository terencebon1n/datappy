import pytest
from fastapi import HTTPException

from backend.api.v1.context import require_city
from backend.domain.gtfs_rt.enums import City


async def test_require_city_returns_city_when_present():
    assert await require_city(City.MONTPELLIER) == City.MONTPELLIER


async def test_require_city_raises_without_header():
    with pytest.raises(HTTPException) as exc_info:
        await require_city(None)
    assert exc_info.value.status_code == 400
