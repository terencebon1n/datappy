import requests
from fastapi import APIRouter
from google.transit import gtfs_realtime_pb2

test_router = APIRouter()


@test_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello Yes"}


@test_router.get("/vehicle-position")
async def vehicle_position() -> dict[str, str]:
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/VehiclePosition.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        print(entity)
    return {"message": "Vehicle Position"}


@test_router.get("/alert")
async def alert() -> dict[str, str]:
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/Alert.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        print(entity)
    return {"message": "Alert"}


@test_router.get("/trip-update")
async def trip_update() -> dict[str, str]:
    feed = gtfs_realtime_pb2.FeedMessage()
    url = "https://data.montpellier3m.fr/TAM_MMM_GTFSRT/TripUpdate.pb"
    response = requests.get(url)
    feed.ParseFromString(response.content)
    for entity in feed.entity:
        print(entity)
    return {"message": "Trip Update"}


@test_router.get("/test")
async def test() -> dict[str, str]:
    return {"message": "test test"}
