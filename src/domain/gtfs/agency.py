from typing import Optional

from pydantic import BaseModel, Field


class Agency(BaseModel):
    id: str = Field(alias="agency_id")
    name: str = Field(alias="agency_name")
    url: Optional[str] = Field(alias="agency_url")
    timezone: str = Field(alias="agency_timezone")
    lang: str = Field(alias="agency_lang")
    phone: Optional[str] = Field(alias="agency_phone")
    fare_url: Optional[str] = Field(alias="agency_fare_url")
