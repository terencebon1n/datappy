from typing import Optional

from pydantic import BaseModel, Field


class Agency(BaseModel):
    id: str = Field(alias="agency_id")
    name: str = Field(alias="agency_name")
    url: Optional[str] = Field(alias="agency_url", default=None)
    timezone: str = Field(alias="agency_timezone")
    lang: Optional[str] = Field(alias="agency_lang", default=None)
    phone: Optional[str] = Field(alias="agency_phone", default=None)
    fare_url: Optional[str] = Field(alias="agency_fare_url", default=None)
    email: Optional[str] = Field(alias="agency_email", default=None)
    cemv_support: Optional[str] = Field(alias="cemv_support", default=None)
