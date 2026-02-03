from pydantic import BaseModel, Field


class StopTime(BaseModel):
    trip_id: str = Field(alias="trip_id")
    arrival_time: str = Field(alias="arrival_time")
    departure_time: str = Field(alias="departure_time")
    stop_id: str = Field(alias="stop_id")
    stop_sequence: int = Field(alias="stop_sequence")
    pickup_type: int = Field(alias="pickup_type")
    drop_off_type: int = Field(alias="drop_off_type")
