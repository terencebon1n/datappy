from typing import Optional

from pydantic import BaseModel, Field


class Route(BaseModel):
    id: str = Field(alias="route_id")
    agency_id: str = Field(alias="agency_id")
    short_name: str = Field(alias="route_short_name")
    long_name: str = Field(alias="route_long_name")
    type: int = Field(alias="route_type")
    color: str = Field(alias="route_color")
    text_color: Optional[str] = Field(alias="route_text_color")
    url: Optional[str] = Field(alias="route_url")
