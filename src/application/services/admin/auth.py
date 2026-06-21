from datetime import datetime, timedelta, timezone

from src.domain.admin.session import AdminSession


class AdminAuthService:
    _SESSION_TTL_HOURS = 24

    def __init__(self, allowed_email: str) -> None:
        self._allowed_email = allowed_email

    def authorize(self, email: str) -> AdminSession:
        if email != self._allowed_email:
            raise PermissionError(f"{email} is not authorized")
        return AdminSession(
            email=email,
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(hours=self._SESSION_TTL_HOURS),
        )
