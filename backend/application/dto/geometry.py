from typing import Optional

from pydantic import BaseModel, Field


class PointDTO(BaseModel):
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")


class RouteShapeDTO(BaseModel):
    direction_id: int = Field(description="Direction ID")
    points: list[PointDTO] = Field(description="Ordered polyline points")


class RouteStopDTO(BaseModel):
    id: str = Field(description="Stop ID")
    name: str = Field(description="Stop Name")
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    code: Optional[str] = Field(default=None, description="Stop code")
    platform_code: Optional[str] = Field(default=None, description="Platform code")
    wheelchair_boarding: Optional[int] = Field(
        default=None, description="GTFS wheelchair_boarding"
    )


class DirectionHeadsignDTO(BaseModel):
    direction_id: int = Field(description="Direction ID")
    headsign: str = Field(description="Most common headsign for the direction")


class RouteGeometryDTO(BaseModel):
    shapes: list[RouteShapeDTO] = Field(description="One polyline per direction")
    stops: list[RouteStopDTO] = Field(description="Stops served by the route")
    direction_headsigns: list[DirectionHeadsignDTO] = Field(
        default_factory=list, description="Headsign shown for each direction"
    )
