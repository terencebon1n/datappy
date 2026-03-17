from typing import Optional

from pydantic import BaseModel, Field, field_validator


class StopTime(BaseModel):
    trip_id: str = Field(alias="trip_id")
    arrival_time: str = Field(alias="arrival_time")
    departure_time: str = Field(alias="departure_time")
    stop_id: str = Field(alias="stop_id")
    stop_sequence: int = Field(alias="stop_sequence")
    stop_headsign: Optional[str] = Field(alias="stop_headsign", default=None)
    pickup_type: Optional[int] = Field(alias="pickup_type", default=None)
    drop_off_type: Optional[int] = Field(alias="drop_off_type", default=None)
    continuous_pickup: Optional[int] = Field(alias="continuous_pickup", default=None)
    continuous_drop_off: Optional[int] = Field(alias="continuous_drop_off", default=None)
    shape_dist_traveled: Optional[float] = Field(alias="shape_dist_traveled", default=None)
    timepoint: Optional[int] = Field(alias="timepoint", default=None)
    pickup_booking_rule_id: Optional[str] = Field(alias="pickup_booking_rule_id", default=None)
    drop_off_booking_rule_id: Optional[str] = Field(alias="drop_off_booking_rule_id", default=None)

    @field_validator("shape_dist_traveled", mode="before")
    @classmethod
    def validate_shape_dist_traveled(cls, v: str | float) -> float:
        if isinstance(v, str):
            if v:
                return float(v)
            return 0
        return v

    @field_validator("timepoint", mode="before")
    @classmethod
    def validate_timepoint(cls, v: str | int) -> int:
        if isinstance(v, str):
            if v:
                return int(v)
            return 0
        return v
