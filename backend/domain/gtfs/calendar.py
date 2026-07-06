from pydantic import BaseModel, Field


class Calendar(BaseModel):
    service_id: str = Field(alias="service_id")
    monday: bool = Field(alias="monday")
    tuesday: bool = Field(alias="tuesday")
    wednesday: bool = Field(alias="wednesday")
    thursday: bool = Field(alias="thursday")
    friday: bool = Field(alias="friday")
    saturday: bool = Field(alias="saturday")
    sunday: bool = Field(alias="sunday")
    start_date: str = Field(alias="start_date")
    end_date: str = Field(alias="end_date")
