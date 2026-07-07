import backend.application.producers.registry as registry_module
from backend.application.producers.registry import ProducerRegistry, ProducerTask
from backend.domain.gtfs_rt.enums import City, FeedType
from backend.infrastructure.config import CityFeedsModel


def test_url_for_each_feed_type():
    feeds = CityFeedsModel(
        gtfs_schedule="s",
        trip_update="tu",
        vehicle_position="vp",
        alert="al",
    )
    assert ProducerRegistry._url_for(feeds, FeedType.ALERT) == "al"
    assert ProducerRegistry._url_for(feeds, FeedType.TRIP_UPDATE) == "tu"
    assert ProducerRegistry._url_for(feeds, FeedType.VEHICLE_POSITION) == "vp"


def test_url_for_unknown_feed_type_returns_none():
    # No ``case`` matches an unknown value -> the match falls through to None.
    feeds = CityFeedsModel(gtfs_schedule="s")
    assert ProducerRegistry._url_for(feeds, object()) is None  # type: ignore[arg-type]


def test_get_all_tasks_skips_missing_urls(monkeypatch):
    # One city fully populated, one with only a schedule (no RT urls) so the
    # ``if url:`` False branch is exercised.
    feeds = {
        City.MONTPELLIER: CityFeedsModel(
            gtfs_schedule="s", trip_update="tu", vehicle_position="vp", alert="al"
        ),
        City.NIMES: CityFeedsModel(gtfs_schedule="s"),
    }
    monkeypatch.setattr(registry_module.settings, "feeds", feeds)

    tasks = ProducerRegistry.get_all_tasks()

    montpellier = [t for t in tasks if t.city == City.MONTPELLIER]
    nimes = [t for t in tasks if t.city == City.NIMES]
    assert len(montpellier) == 3  # all three RT feeds
    assert nimes == []  # no RT urls -> no tasks
    assert all(isinstance(t, ProducerTask) for t in tasks)


def test_get_tasks_filters(monkeypatch):
    feeds = {
        City.MONTPELLIER: CityFeedsModel(
            gtfs_schedule="s", trip_update="tu", vehicle_position="vp", alert="al"
        ),
        City.BORDEAUX: CityFeedsModel(
            gtfs_schedule="s", trip_update="tu", vehicle_position="vp", alert="al"
        ),
    }
    monkeypatch.setattr(registry_module.settings, "feeds", feeds)

    assert len(ProducerRegistry.get_tasks()) == 6  # 2 cities x 3 feeds
    by_city = ProducerRegistry.get_tasks(city=City.MONTPELLIER)
    assert {t.city for t in by_city} == {City.MONTPELLIER}
    by_feed = ProducerRegistry.get_tasks(feed=FeedType.TRIP_UPDATE)
    assert {t.feed_type for t in by_feed} == {FeedType.TRIP_UPDATE}
    both = ProducerRegistry.get_tasks(city=City.BORDEAUX, feed=FeedType.ALERT)
    assert len(both) == 1
    assert both[0].city == City.BORDEAUX and both[0].feed_type == FeedType.ALERT


def test_producer_task_is_frozen():
    task = ProducerTask(city=City.NIMES, feed_type=FeedType.ALERT, url="u")
    assert task.url == "u"
