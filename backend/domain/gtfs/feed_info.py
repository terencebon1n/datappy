from typing import Optional

from pydantic import BaseModel, Field


class FeedInfo(BaseModel):
    publisher_name: str = Field(alias="feed_publisher_name")
    publisher_url: str = Field(alias="feed_publisher_url")
    default_lang: Optional[str] = Field(alias="default_lang", default=None)
    start_date: Optional[str] = Field(alias="feed_start_date", default=None)
    end_date: Optional[str] = Field(alias="feed_end_date", default=None)
    version: str = Field(alias="feed_version")
    contact_email: Optional[str] = Field(alias="feed_contact_email", default=None)
    contact_url: Optional[str] = Field(alias="feed_contact_url", default=None)
