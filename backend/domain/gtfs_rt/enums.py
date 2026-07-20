from enum import StrEnum


class City(StrEnum):
    MONTPELLIER = "montpellier"
    BORDEAUX = "bordeaux"
    TOULOUSE = "toulouse"
    NIMES = "nimes"


class FeedType(StrEnum):
    TRIP_UPDATE = "TripUpdate"
    VEHICLE_POSITION = "VehiclePosition"
    ALERT = "Alert"

    def topic(self, city: City) -> str:
        return f"{city}.{self.value}"


class _FallbackStrEnum(StrEnum):
    @classmethod
    def _missing_(cls, value: object) -> "_FallbackStrEnum":
        return cls(cls._fallback())

    @classmethod
    def _fallback(cls) -> str:
        raise NotImplementedError


class AlertCause(_FallbackStrEnum):
    UNKNOWN_CAUSE = "UNKNOWN_CAUSE"
    OTHER_CAUSE = "OTHER_CAUSE"
    TECHNICAL_PROBLEM = "TECHNICAL_PROBLEM"
    STRIKE = "STRIKE"
    DEMONSTRATION = "DEMONSTRATION"
    ACCIDENT = "ACCIDENT"
    HOLIDAY = "HOLIDAY"
    WEATHER = "WEATHER"
    MAINTENANCE = "MAINTENANCE"
    CONSTRUCTION = "CONSTRUCTION"
    POLICE_ACTIVITY = "POLICE_ACTIVITY"
    MEDICAL_EMERGENCY = "MEDICAL_EMERGENCY"

    @classmethod
    def _fallback(cls) -> str:
        return cls.UNKNOWN_CAUSE.value


class AlertEffect(_FallbackStrEnum):
    NO_SERVICE = "NO_SERVICE"
    REDUCED_SERVICE = "REDUCED_SERVICE"
    SIGNIFICANT_DELAYS = "SIGNIFICANT_DELAYS"
    DETOUR = "DETOUR"
    ADDITIONAL_SERVICE = "ADDITIONAL_SERVICE"
    MODIFIED_SERVICE = "MODIFIED_SERVICE"
    OTHER_EFFECT = "OTHER_EFFECT"
    UNKNOWN_EFFECT = "UNKNOWN_EFFECT"
    STOP_MOVED = "STOP_MOVED"
    NO_EFFECT = "NO_EFFECT"
    ACCESSIBILITY_ISSUE = "ACCESSIBILITY_ISSUE"

    @classmethod
    def _fallback(cls) -> str:
        return cls.UNKNOWN_EFFECT.value


class AlertSeverity(_FallbackStrEnum):
    UNKNOWN_SEVERITY = "UNKNOWN_SEVERITY"
    INFO = "INFO"
    WARNING = "WARNING"
    SEVERE = "SEVERE"

    @classmethod
    def _fallback(cls) -> str:
        return cls.UNKNOWN_SEVERITY.value

    @property
    def rank(self) -> int:
        return _SEVERITY_RANKS[self]


_SEVERITY_RANKS = {
    AlertSeverity.SEVERE: 0,
    AlertSeverity.WARNING: 1,
    AlertSeverity.INFO: 2,
    AlertSeverity.UNKNOWN_SEVERITY: 3,
}
