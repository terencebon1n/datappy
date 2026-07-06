from datetime import datetime

from pydantic import BaseModel


class AdminSession(BaseModel):
    email: str
    expires_at: datetime
