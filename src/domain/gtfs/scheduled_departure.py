from pydantic import BaseModel


class ScheduledDeparture(BaseModel):
    trip_id: str
    departure_time: str
    arrival_time: str
