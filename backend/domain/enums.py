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
