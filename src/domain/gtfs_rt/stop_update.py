from datetime import datetime, timedelta, timezone

from pydantic import BaseModel


class StopUpdate(BaseModel):
    trip_id: str
    timestamp: str
    departure_time: int
    departure_delay: int
    arrival_time: int
    arrival_delay: int

    def _parse_timestamp(self, v: str) -> datetime:
        formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(v, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        raise ValueError(f"Invalid timestamp format: {v}")

    def is_stale(self, reference_time: datetime) -> bool:
        if self._parse_timestamp(self.timestamp) < reference_time - timedelta(
            minutes=5
        ):
            return True
        if self.departure_time < int(
            (reference_time - timedelta(minutes=1)).timestamp()
        ):
            return True
        return False
