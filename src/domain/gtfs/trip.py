from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class Trip(BaseModel):
    route_id: str = Field(alias="route_id")
    service_id: str = Field(alias="service_id")
    id: str = Field(alias="trip_id")
    headsign: str = Field(alias="trip_headsign")
    short_name: str = Field(alias="trip_short_name")
    direction_id: int = Field(alias="direction_id")
    wheelchair_accessible: Optional[bool] = Field(alias="wheelchair_accessible")
    bikes_allowed: Optional[bool] = Field(alias="bikes_allowed")

    @field_validator("bikes_allowed", mode="before")
    @classmethod
    def ensure_valid_bikes_allowed(cls, v: Any) -> bool:
        if not isinstance(v, bool):
            return False
        return v
