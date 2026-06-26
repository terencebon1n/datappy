from pydantic import BaseModel, Field


class RouteIdDTO(BaseModel):
    route_id: str = Field(description="Route ID")


class ConveyanceDTO(BaseModel):
    id: str = Field(description="Route ID")
    short_name: str = Field(description="Route short name")
    long_name: str = Field(description="Route long name")
    color: str = Field(description="Route color")
    type: int = Field(description="GTFS route_type")
    type_name: str = Field(description="Human-readable route type")
