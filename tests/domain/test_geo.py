import math

import pytest
from pydantic import ValidationError

from backend.domain.gtfs.geo import EARTH_RADIUS_METERS, Coordinates

_COMEDIE = Coordinates(latitude=43.608490, longitude=3.879568)
_GARE_SAINT_ROCH = Coordinates(latitude=43.604900, longitude=3.880600)


def test_distance_to_self_is_zero():
    assert _COMEDIE.distance_to(_COMEDIE) == 0.0


def test_distance_to_is_symmetric():
    assert _COMEDIE.distance_to(_GARE_SAINT_ROCH) == pytest.approx(
        _GARE_SAINT_ROCH.distance_to(_COMEDIE)
    )


def test_distance_between_known_montpellier_stops():
    distance = _COMEDIE.distance_to(_GARE_SAINT_ROCH)

    assert distance == pytest.approx(408, abs=5)


def test_distance_across_a_full_meridian_is_half_circumference():
    north = Coordinates(latitude=90.0, longitude=0.0)
    south = Coordinates(latitude=-90.0, longitude=0.0)

    assert north.distance_to(south) == pytest.approx(math.pi * EARTH_RADIUS_METERS)


def test_bounding_box_contains_the_origin():
    box = _COMEDIE.bounding_box(800)

    assert box.min_latitude < _COMEDIE.latitude < box.max_latitude
    assert box.min_longitude < _COMEDIE.longitude < box.max_longitude


def test_bounding_box_is_wider_in_longitude_than_latitude_away_from_equator():
    box = _COMEDIE.bounding_box(800)

    latitude_span = box.max_latitude - box.min_latitude
    longitude_span = box.max_longitude - box.min_longitude

    assert longitude_span > latitude_span


def test_bounding_box_covers_every_point_within_the_radius():
    box = _COMEDIE.bounding_box(1000)
    due_north = Coordinates(latitude=_COMEDIE.latitude + 0.008, longitude=3.879568)
    due_east = Coordinates(latitude=43.608490, longitude=_COMEDIE.longitude + 0.011)

    for point in (due_north, due_east):
        assert _COMEDIE.distance_to(point) < 1000
        assert box.min_latitude <= point.latitude <= box.max_latitude
        assert box.min_longitude <= point.longitude <= box.max_longitude


def test_bounding_box_at_the_pole_spans_every_longitude():
    box = Coordinates(latitude=90.0, longitude=0.0).bounding_box(800)

    assert (box.min_longitude, box.max_longitude) == (-180.0, 180.0)
    assert box.max_latitude == 90.0


def test_bounding_box_across_the_antimeridian_spans_every_longitude():
    box = Coordinates(latitude=0.0, longitude=179.999).bounding_box(800)

    assert (box.min_longitude, box.max_longitude) == (-180.0, 180.0)


def test_bounding_box_clamps_latitude_to_the_south_pole():
    box = Coordinates(latitude=-89.999, longitude=0.0).bounding_box(800)

    assert box.min_latitude == -90.0


@pytest.mark.parametrize(
    "latitude,longitude",
    [(91.0, 0.0), (-91.0, 0.0), (0.0, 181.0), (0.0, -181.0)],
)
def test_coordinates_reject_out_of_range_values(latitude, longitude):
    with pytest.raises(ValidationError):
        Coordinates(latitude=latitude, longitude=longitude)
