from enum import IntEnum, StrEnum


class RouteTypeId(IntEnum):
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_CAR = 5
    GONDOLA = 6
    FUNICULAR = 7


class RouteTypeName(StrEnum):
    TRAM = "Tram"
    SUBWAY = "Subway"
    RAIL = "Rail"
    BUS = "Bus"
    FERRY = "Ferry"
    CABLE_CAR = "Cable Car"
    GONDOLA = "Gondola"
    FUNICULAR = "Funicular"


def route_type_name(route_type: int) -> str:
    """Human-readable label for a GTFS route_type.

    GTFS allows extended route types beyond the standard 0-7, so fall back
    gracefully instead of raising on an unknown value.
    """
    try:
        return RouteTypeName[RouteTypeId(route_type).name].value
    except ValueError:
        return "Autre"
