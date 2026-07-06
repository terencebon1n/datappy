from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Trip(BaseModel):
    route_id: str = Field(alias="route_id")
    service_id: str = Field(alias="service_id")
    id: str = Field(alias="trip_id")
    headsign: Optional[str] = Field(alias="trip_headsign", default=None)
    short_name: Optional[str] = Field(alias="trip_short_name", default=None)
    direction_id: Optional[int] = Field(alias="direction_id", default=0)
    block_id: Optional[str] = Field(alias="block_id", default=None)
    shape_id: Optional[str] = Field(alias="shape_id", default=None)
    wheelchair_accessible: Optional[int] = Field(
        alias="wheelchair_accessible", default=None
    )
    bikes_allowed: Optional[int] = Field(alias="bikes_allowed", default=None)
    cars_allowed: Optional[int] = Field(alias="cars_allowed", default=None)

    @field_validator(
        "wheelchair_accessible", "bikes_allowed", "cars_allowed", mode="before"
    )
    @classmethod
    def validate_accessibility(cls, v: str | int) -> int:
        if isinstance(v, str):
            if v:
                return int(v)
            return 0
        return v
