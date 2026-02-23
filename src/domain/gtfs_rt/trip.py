from pydantic import BaseModel


class Trip(BaseModel):
    id: str
    schedule_relationship: int
    route_id: str
    direction_id: int
