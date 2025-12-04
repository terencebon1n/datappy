from dataclasses import dataclass


@dataclass(frozen=True)
class Period:
    start: int
    end: int
