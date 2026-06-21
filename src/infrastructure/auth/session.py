from datetime import datetime

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.domain.admin.session import AdminSession

_SALT = "admin-session"


class SessionManager:
    def __init__(self, secret_key: str, max_age: int = 86400) -> None:
        self._serializer = URLSafeTimedSerializer(secret_key)
        self._max_age = max_age

    def encode(self, session: AdminSession) -> str:
        return self._serializer.dumps(
            {"email": session.email, "expires_at": session.expires_at.isoformat()},
            salt=_SALT,
        )

    def decode(self, token: str) -> AdminSession:
        try:
            data = self._serializer.loads(token, salt=_SALT, max_age=self._max_age)
            return AdminSession(
                email=data["email"],
                expires_at=datetime.fromisoformat(data["expires_at"]),
            )
        except SignatureExpired:
            raise ValueError("Session expired")
        except BadSignature:
            raise ValueError("Invalid session")
