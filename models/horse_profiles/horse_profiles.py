from datetime import datetime

from pydantic import BaseModel, Field

from utils.date_time import get_current_utc_datetime


class HorseProfileInternal(BaseModel):
    horse_name: str
    customer_transfer_id: str
    age: int
    health_info: str
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
