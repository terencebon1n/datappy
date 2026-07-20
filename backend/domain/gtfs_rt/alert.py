from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity

_NO_TRANSLATION = "No Translation"


class Period(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

    def contains(self, at: int) -> bool:
        if self.start and at < self.start:
            return False
        if self.end and at > self.end:
            return False
        return True


class InformedEntity(BaseModel):
    agency_id: Optional[str] = None
    route_id: Optional[str] = None
    route_type: Optional[int] = None
    direction_id: Optional[int] = None
    stop_id: Optional[str] = None

    @field_validator("agency_id", "route_id", "stop_id", mode="before")
    @classmethod
    def discard_blank(cls, v: Optional[str]) -> Optional[str]:
        return v or None

    @property
    def is_network_wide(self) -> bool:
        return self.route_id is None and self.stop_id is None

    def concerns(
        self, route_id: str, direction_id: Optional[int], stop_id: Optional[str]
    ) -> bool:
        if self.is_network_wide:
            return True
        if self.route_id is not None and self.route_id != route_id:
            return False
        if self.direction_id is not None and self.direction_id != direction_id:
            return False
        if self.stop_id is not None and self.stop_id != stop_id:
            return False
        return True


class Alert(BaseModel):
    id: str
    active_periods: List[Period] = Field(default_factory=list)
    informed_entities: List[InformedEntity] = Field(default_factory=list)
    cause: AlertCause = AlertCause.UNKNOWN_CAUSE
    effect: AlertEffect = AlertEffect.UNKNOWN_EFFECT
    severity: AlertSeverity = AlertSeverity.UNKNOWN_SEVERITY
    header_text: str = "No Header"
    description_text: str = "No Description"
    url: Optional[str] = None

    @field_validator("header_text", "description_text", mode="before")
    @classmethod
    def handle_missing_translation(cls, v: str) -> str:
        if not v or v.strip() == "":
            return _NO_TRANSLATION
        return v

    @field_validator("url", mode="before")
    @classmethod
    def discard_blank_url(cls, v: Optional[str]) -> Optional[str]:
        return v or None

    def is_active(self, at: int) -> bool:
        if not self.active_periods:
            return True
        return any(period.contains(at) for period in self.active_periods)

    def concerns(
        self, route_id: str, direction_id: Optional[int], stop_id: Optional[str]
    ) -> bool:
        return any(
            entity.concerns(route_id, direction_id, stop_id)
            for entity in self.informed_entities
        )
