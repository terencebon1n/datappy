from pydantic import BaseModel, Field


class Transfer(BaseModel):
    from_stop_id: str = Field(alias="from_stop_id")
    to_stop_id: str = Field(alias="to_stop_id")
    transfer_type: int = Field(alias="transfer_type")
