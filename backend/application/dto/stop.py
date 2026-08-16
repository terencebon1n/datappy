from pydantic import BaseModel, Field

from backend.application.dto.route import ConveyanceDTO
from backend.domain.gtfs_rt.enums import City


class StopNameDTO(BaseModel):
    name: str = Field(description="Stop Name")


class NearbyQueryDTO(BaseModel):
    latitude: float = Field(description="Latitude", ge=-90.0, le=90.0)
    longitude: float = Field(description="Longitude", ge=-180.0, le=180.0)
    radius_m: int = Field(
        default=800, description="Search radius in meters", gt=0, le=5000
    )
    limit: int = Field(default=10, description="Maximum stops returned", gt=0, le=50)


class NearbyStopDTO(BaseModel):
    name: str = Field(description="Stop Name")
    distance_m: int = Field(description="Distance from the query point in meters")
    latitude: float = Field(description="Latitude of the nearest matching platform")
    longitude: float = Field(description="Longitude of the nearest matching platform")
    routes: list[ConveyanceDTO] = Field(description="Routes serving the stop")


class TransitPathDTO(BaseModel):
    city: City = Field(description="City")
    route_id: str = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    stop_id__origin: str = Field(description="Stop ID Origin")
    stop_id__destination: str = Field(description="Stop ID Destination")
