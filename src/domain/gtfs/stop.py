from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class Stop(BaseModel):
    id: str = Field(alias="stop_id")
    code: int = Field(alias="stop_code")
    name: str = Field(alias="stop_name")
    tts_name: str = Field(alias="tts_stop_name")
    latitude: float = Field(alias="stop_lat")
    longitude: float = Field(alias="stop_lon")
    location_type: str = Field(alias="location_type")
    parent_station: Optional[str] = Field(alias="parent_station")
    wheelchair_boarding: int = Field(alias="wheelchair_boarding")

    @field_validator("code", mode="before")
    @classmethod
    def ensure_valid_code(cls, v: Any) -> int:
        if not isinstance(v, int):
            return 0
        return v
