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


class RouteGeometryDTO(BaseModel):
    shapes: list[RouteShapeDTO] = Field(description="One polyline per direction")
    stops: list[RouteStopDTO] = Field(description="Stops served by the route")
