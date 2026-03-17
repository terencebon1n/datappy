from typing import Optional

from pydantic import BaseModel, Field


class Route(BaseModel):
    id: str = Field(alias="route_id")
    agency_id: str = Field(alias="agency_id")
    short_name: str = Field(alias="route_short_name")
    long_name: str = Field(alias="route_long_name")
    description: Optional[str] = Field(alias="route_desc", default=None)
    type: int = Field(alias="route_type")
    url: Optional[str] = Field(alias="route_url", default=None)
    color: Optional[str] = Field(alias="route_color", default=None)
    text_color: Optional[str] = Field(alias="route_text_color", default=None)
    sort_order: Optional[int] = Field(alias="route_sort_order", default=None)
    continuous_pickup: Optional[int] = Field(alias="continuous_pickup", default=None)
    continuous_drop_off: Optional[int] = Field(
        alias="continuous_drop_off", default=None
    )
    network_id: Optional[str] = Field(alias="network_id", default=None)
    cemv_support: Optional[str] = Field(alias="cemv_support", default=None)
