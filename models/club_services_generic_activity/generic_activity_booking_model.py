from datetime import datetime
from typing import Optional

from bson import ObjectId
from data.db import PyObjectId
from pydantic import BaseModel, Field


class GenericActivityBooking(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    user_id: str
    generic_activity_service_id: str
    trainer_id: str
    selected_date: datetime
    pricing_option: float
    number_of_visitors: int

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
