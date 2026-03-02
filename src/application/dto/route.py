from pydantic import BaseModel, Field

from src.domain.enums import RouteTypeId, RouteTypeName


class RouteTypeDTO(BaseModel):
    id: RouteTypeId = Field(description="Route Type ID")
    name: RouteTypeName = Field(description="Route Type Name")


class RouteIdDTO(BaseModel):
    route_id: str = Field(description="Route ID")


class ConveyanceDTO(BaseModel):
    id: str = Field(description="Route ID")
    short_name: str = Field(description="Route short name")
    long_name: str = Field(description="Route long name")
