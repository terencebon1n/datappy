from ..base import SparkColumns


class StopTimeColumns(SparkColumns):
    STOP_ID = "id"
    ARRIVAL_DELAY = "arrival_delay"
    ARRIVAL_TIME = "arrival_time"
    DEPARTURE_DELAY = "departure_delay"
    DEPARTURE_TIME = "departure_time"
    SCHEDULE_RELATIONSHIP = "schedule_relationship"
