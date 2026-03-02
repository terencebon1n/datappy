from pydantic import BaseModel, Field


class StopNameDTO(BaseModel):
    name: str = Field(description="Stop Name")


class TransitPathDTO(BaseModel):
    route_id: int = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    stop_id: int = Field(description="Stop ID")
