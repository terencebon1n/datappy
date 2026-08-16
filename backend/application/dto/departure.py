from typing import Optional

from pydantic import BaseModel, Field

from backend.domain.gtfs_rt.enums import City


class StopDeparturePathDTO(BaseModel):
    city: City = Field(description="City")
    stop_id: str = Field(description="Stop ID")
    limit: int = Field(
        default=4, description="Maximum departures per destination", gt=0, le=20
    )


class StopDepartureDTO(BaseModel):
    trip_id: str = Field(description="Trip ID")
    route_id: str = Field(description="Route ID")
    route_short_name: str = Field(description="Route short name")
    route_color: Optional[str] = Field(default=None, description="Route color")
    route_type: int = Field(description="GTFS route_type")
    direction_id: int = Field(description="Direction ID")
    headsign: str = Field(description="Destination shown on the vehicle")
    departure_time: int = Field(description="Departure epoch seconds")
    departure_delay: int = Field(description="Delay in seconds")
    is_realtime: bool = Field(description="Whether the departure is realtime")
