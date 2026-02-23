from pydantic import BaseModel


class StopUpdate(BaseModel):
    trip_id: str
    timestamp: str
    departure_time: int
    departure_delay: int
    arrival_time: int
    arrival_delay: int
