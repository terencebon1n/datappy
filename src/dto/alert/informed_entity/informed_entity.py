from dataclasses import dataclass


@dataclass(frozen=True)
class InformedEntity:
    route_id: str
