from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Period(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None


class InformedEntity(BaseModel):
    route_id: Optional[str] = None
    stop_id: Optional[str] = None


class Alert(BaseModel):
    id: str
    active_periods: List[Period] = Field(default_factory=list)
    informed_entities: List[InformedEntity] = Field(default_factory=list)
    header_text: str = "No Header"
    description_text: str = "No Description"

    @field_validator("header_text", "description_text", mode="before")
    @classmethod
    def handle_missing_translation(cls, v: str) -> str:
        if not v or v.strip() == "":
            return "No Translation"
        return v
