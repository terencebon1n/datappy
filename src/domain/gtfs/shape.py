from typing import Optional

from pydantic import BaseModel, Field


class Shape(BaseModel):
    id: str = Field(alias="shape_id")
    latitude: float = Field(alias="shape_pt_lat")
    longitude: float = Field(alias="shape_pt_lon")
    sequence: int = Field(alias="shape_pt_sequence")
    distance_traveled: Optional[float] = Field(
        alias="shape_dist_traveled", default=None
    )
