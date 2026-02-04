from pydantic import BaseModel


class Trip(BaseModel):
    id: str
    schedule_relationship: str
    route_id: str
    direction_id: int
