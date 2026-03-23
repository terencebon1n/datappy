from pydantic import BaseModel, Field, field_validator


class StopNameDTO(BaseModel):
    name: str = Field(description="Stop Name")


class TransitPathDTO(BaseModel):
    route_id: str = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    stop_id__origin: str = Field(description="Stop ID Origin")
    stop_id__destination: str = Field(description="Stop ID Destination")

    @field_validator(
        "route_id", "stop_id__origin", "stop_id__destination", mode="before"
    )
    @classmethod
    def validate_id(cls, v: str) -> str:
        return v.replace(":", "_")
