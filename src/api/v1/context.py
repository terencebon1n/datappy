from typing import Annotated

from fastapi import Header, HTTPException

from src.api import async_db_manager
from src.domain.gtfs_rt.enums import City


async def set_city_context(city: Annotated[City | None, Header()] = None) -> City:
    if not city:
        raise HTTPException(
            status_code=400, detail="City header is required to make request"
        )
    async_db_manager.set_schema(city)
    return city
