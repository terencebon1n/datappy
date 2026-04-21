from datetime import datetime, timedelta, timezone

from pydantic import BaseModel


class StopUpdate(BaseModel):
    trip_id: str
    timestamp: int
    departure_time: int
    departure_delay: int
    arrival_time: int
    arrival_delay: int

    def _parse_timestamp(self, v: int) -> datetime:
        try:
            ts = float(v)
            if ts > 1e11:
                ts /= 1000
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, TypeError):
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
