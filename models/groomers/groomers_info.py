from datetime import datetime

from pydantic import BaseModel, Field

from utils.date_time import get_current_utc_datetime


class GroomersInfoInternal(BaseModel):
    groomer_name: str
    contact_number: str
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
