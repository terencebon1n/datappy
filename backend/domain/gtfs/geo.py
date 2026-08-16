import math

from pydantic import BaseModel, Field

EARTH_RADIUS_METERS = 6_371_008.8

_POLE_COS_LATITUDE_EPSILON = 1e-12


class BoundingBox(BaseModel):
    min_latitude: float
    max_latitude: float
    min_longitude: float
    max_longitude: float


class Coordinates(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)

    def distance_to(self, other: "Coordinates") -> float:
        origin_latitude = math.radians(self.latitude)
        target_latitude = math.radians(other.latitude)
        delta_latitude = target_latitude - origin_latitude
        delta_longitude = math.radians(other.longitude - self.longitude)

        chord = (
            math.sin(delta_latitude / 2) ** 2
            + math.cos(origin_latitude)
            * math.cos(target_latitude)
            * math.sin(delta_longitude / 2) ** 2
        )
        return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(min(1.0, chord)))

    def bounding_box(self, radius_meters: float) -> BoundingBox:
        latitude_span = math.degrees(radius_meters / EARTH_RADIUS_METERS)
        cos_latitude = math.cos(math.radians(self.latitude))
        longitude_span = (
            math.inf
            if cos_latitude <= _POLE_COS_LATITUDE_EPSILON
            else math.degrees(radius_meters / (EARTH_RADIUS_METERS * cos_latitude))
        )

        wraps_longitude = (
            self.longitude - longitude_span < -180.0
            or self.longitude + longitude_span > 180.0
        )

        return BoundingBox(
            min_latitude=max(self.latitude - latitude_span, -90.0),
            max_latitude=min(self.latitude + latitude_span, 90.0),
            min_longitude=-180.0
            if wraps_longitude
            else self.longitude - longitude_span,
            max_longitude=180.0 if wraps_longitude else self.longitude + longitude_span,
        )
