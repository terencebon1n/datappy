from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    latitude: float
    longitude: float
    bearing: int
    speed: int
