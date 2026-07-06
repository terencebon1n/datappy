from typing import Optional

from pydantic import BaseModel, Field


class Stop(BaseModel):
    id: str = Field(alias="stop_id")
    code: Optional[str] = Field(alias="stop_code", default=None)
    name: str = Field(alias="stop_name")
    tts_name: Optional[str] = Field(alias="tts_stop_name", default=None)
    description: Optional[str] = Field(alias="stop_desc", default=None)
    latitude: float = Field(alias="stop_lat")
    longitude: float = Field(alias="stop_lon")
    zone_id: Optional[str] = Field(alias="zone_id", default=None)
    url: Optional[str] = Field(alias="stop_url", default=None)
    location_type: Optional[str] = Field(alias="location_type", default=None)
    parent_station: Optional[str] = Field(alias="parent_station")
    timezone: Optional[str] = Field(alias="stop_timezone", default=None)
    wheelchair_boarding: Optional[int] = Field(
        alias="wheelchair_boarding", default=None
    )
    level_id: Optional[str] = Field(alias="level_id", default=None)
    platform_code: Optional[str] = Field(alias="platform_code", default=None)
