from __future__ import annotations

from pydantic import BaseModel, Field


class CalendarDate(BaseModel):
    service_id: str = Field(alias="service_id")
    date: str = Field(alias="date")
    exception_type: int = Field(alias="exception_type")
