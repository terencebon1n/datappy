from enum import StrEnum


class ServiceCommand(StrEnum):
    API = "api"
    CONSUMER = "consumer"
    PRODUCER = "producer"
    POPULATE = "populate"
