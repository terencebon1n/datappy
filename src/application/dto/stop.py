from pydantic import BaseModel, Field

from src.domain.gtfs_rt.enums import City


class StopNameDTO(BaseModel):
    name: str = Field(description="Stop Name")


class TransitPathDTO(BaseModel):
    city: City = Field(description="City")
    route_id: str = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    stop_id__origin: str = Field(description="Stop ID Origin")
    stop_id__destination: str = Field(description="Stop ID Destination")
