"""Alert domain rules: activity windows, entity linking and severity ordering."""

import pytest

from backend.domain.gtfs_rt.alert import Alert, InformedEntity, Period
from backend.domain.gtfs_rt.enums import AlertCause, AlertEffect, AlertSeverity


@pytest.mark.parametrize(
    ("period", "at", "expected"),
    [
        (Period(start=10, end=20), 15, True),
        (Period(start=10, end=20), 5, False),
        (Period(start=10, end=20), 25, False),
        (Period(start=10, end=20), 10, True),
        (Period(start=10, end=20), 20, True),
        (Period(start=None, end=20), 1, True),
        (Period(start=10, end=None), 9999, True),
        (Period(), 0, True),
    ],
)
def test_period_contains(period, at, expected):
    assert period.contains(at) is expected


def test_alert_without_periods_is_always_active():
    assert Alert(id="a").is_active(0) is True


def test_alert_is_active_when_any_period_matches():
    alert = Alert(
        id="a",
        active_periods=[Period(start=10, end=20), Period(start=100, end=200)],
    )
    assert alert.is_active(150) is True
    assert alert.is_active(50) is False


@pytest.mark.parametrize(
    ("entity", "expected"),
    [
        (InformedEntity(route_id="R1"), True),
        (InformedEntity(route_id="R2"), False),
        (InformedEntity(stop_id="S1"), True),
        (InformedEntity(stop_id="S9"), False),
        (InformedEntity(route_id="R1", stop_id="S1"), True),
        (InformedEntity(route_id="R1", stop_id="S9"), False),
        (InformedEntity(route_id="R1", direction_id=0), True),
        (InformedEntity(route_id="R1", direction_id=1), False),
        (InformedEntity(agency_id="AG"), True),
        (InformedEntity(), True),
    ],
)
def test_informed_entity_concerns(entity, expected):
    assert entity.concerns("R1", 0, "S1") is expected


def test_blank_proto_strings_become_none():
    entity = InformedEntity(agency_id="", route_id="", stop_id="")
    assert entity.agency_id is None
    assert entity.route_id is None
    assert entity.is_network_wide is True


def test_alert_concerns_requires_at_least_one_matching_entity():
    alert = Alert(
        id="a",
        informed_entities=[InformedEntity(route_id="R9"), InformedEntity(stop_id="S1")],
    )
    assert alert.concerns("R1", 0, "S1") is True
    assert alert.concerns("R1", 0, "S2") is False


def test_alert_without_entities_concerns_nothing():
    assert Alert(id="a").concerns("R1", 0, "S1") is False


def test_alert_url_blank_becomes_none():
    assert Alert(id="a", url="").url is None
    assert Alert(id="a", url="https://x.fr").url == "https://x.fr"


@pytest.mark.parametrize(
    ("enum_cls", "fallback"),
    [
        (AlertCause, AlertCause.UNKNOWN_CAUSE),
        (AlertEffect, AlertEffect.UNKNOWN_EFFECT),
        (AlertSeverity, AlertSeverity.UNKNOWN_SEVERITY),
    ],
)
def test_unknown_enum_values_fall_back(enum_cls, fallback):
    assert enum_cls("SOMETHING_NEW") is fallback


def test_severity_rank_orders_most_urgent_first():
    ranked = sorted(AlertSeverity, key=lambda severity: severity.rank)
    assert ranked == [
        AlertSeverity.SEVERE,
        AlertSeverity.WARNING,
        AlertSeverity.INFO,
        AlertSeverity.UNKNOWN_SEVERITY,
    ]


def test_fallback_base_requires_override():
    from backend.domain.gtfs_rt.enums import _FallbackStrEnum

    with pytest.raises(NotImplementedError):
        _FallbackStrEnum._fallback()
