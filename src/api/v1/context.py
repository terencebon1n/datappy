from typing import Annotated

from fastapi import Header, HTTPException

from src.domain.gtfs_rt.enums import City


async def require_city(city: Annotated[City | None, Header()] = None) -> City:
    if not city:
        raise HTTPException(
            status_code=400, detail="City header is required to make request"
        )
    return city
