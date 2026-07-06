from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Transfer(BaseModel):
    from_stop_id: str = Field(alias="from_stop_id")
    to_stop_id: str = Field(alias="to_stop_id")
    from_route_id: Optional[str] = Field(alias="from_route_id", default=None)
    to_route_id: Optional[str] = Field(alias="to_route_id", default=None)
    from_trip_id: Optional[str] = Field(alias="from_trip_id", default=None)
    to_trip_id: Optional[str] = Field(alias="to_trip_id", default=None)
    transfer_type: int = Field(alias="transfer_type")
    min_transfer_time: Optional[int] = Field(alias="min_transfer_time", default=None)

    @field_validator("min_transfer_time", mode="before")
    @classmethod
    def validate_min_transfer_time(cls, v: str | int) -> int:
        if isinstance(v, str):
            if v:
                return int(v)
            return 0
        return v
