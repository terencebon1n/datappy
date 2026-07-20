from typing import Optional

from pydantic import BaseModel, Field

from backend.domain.gtfs_rt.alert import Alert
from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity, City


class AlertPathDTO(BaseModel):
    city: City = Field(description="City")
    route_id: str = Field(description="Route ID")
    direction_id: Optional[int] = Field(default=None, description="Direction ID")
    stop_id: Optional[str] = Field(default=None, description="Stop ID")


class AlertDTO(BaseModel):
    id: str = Field(description="Alert ID")
    cause: AlertCause = Field(description="Alert Cause")
    effect: AlertEffect = Field(description="Alert Effect")
    severity: AlertSeverity = Field(description="Alert Severity")
    header_text: str = Field(description="Alert Header")
    description_text: str = Field(description="Alert Description")
    url: Optional[str] = Field(default=None, description="Alert URL")

    @classmethod
    def from_domain(cls, alert: Alert) -> "AlertDTO":
        return cls(
            id=alert.id,
            cause=alert.cause,
            effect=alert.effect,
            severity=alert.severity,
            header_text=alert.header_text,
            description_text=alert.description_text,
            url=alert.url,
        )
