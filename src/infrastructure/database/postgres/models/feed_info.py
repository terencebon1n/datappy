from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.postgres.base import GTFSModelBase


class FeedInfoModel(GTFSModelBase):
    __tablename__ = "feed_info"

    publisher_name: Mapped[str] = mapped_column(String, primary_key=True)
    publisher_url: Mapped[str] = mapped_column(String)
    default_lang: Mapped[Optional[str]] = mapped_column(String)
    start_date: Mapped[Optional[str]] = mapped_column(String)
    end_date: Mapped[Optional[str]] = mapped_column(String)
    version: Mapped[str] = mapped_column(String, primary_key=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String)
    contact_url: Mapped[Optional[str]] = mapped_column(String)
