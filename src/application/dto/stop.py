from pydantic import BaseModel, Field, field_validator


class StopNameDTO(BaseModel):
    name: str = Field(description="Stop Name")


class TransitPathDTO(BaseModel):
    route_id: str = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    stop_id: str = Field(description="Stop ID")

    @field_validator("route_id", "stop_id", mode="before")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return v.replace(":", "_")
