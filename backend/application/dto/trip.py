from pydantic import BaseModel, Field


class PathDTO(BaseModel):
    route_id: str = Field(description="Route ID")
    stop_name__origin: str = Field(description="Stop Origin")
    stop_name__destination: str = Field(description="Stop Destination")


class DirectionDTO(BaseModel):
    direction_id: int = Field(description="Direction ID")
    stop_id__origin: str = Field(description="Stop ID Origin")
    stop_id__destination: str = Field(description="Stop ID Destination")
