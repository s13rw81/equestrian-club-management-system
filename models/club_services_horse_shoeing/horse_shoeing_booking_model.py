from datetime import datetime
from typing import Optional

from bson import ObjectId
from data.db import PyObjectId
from pydantic import BaseModel, Field


# class RidingLessonBooking(BaseModel):
#     id: Optional[PyObjectId] = Field(alias = '_id', default = None)
#     lesson_service: RidingLessonService
#     rider: UserExternal
#     trainer: UserExternal
#     lesson_datetime: datetime = Field(default_factory = get_current_utc_datetime)
#     booking_datetime: datetime = Field(default_factory = get_current_utc_datetime)
#     update_datetime: datetime = Field(default_factory = get_current_utc_datetime)
#     venue: Address
#     payment_status: str  # TODO: change to an ENUM
#     booking_status: str  # TODO: change to an ENUM
#
#     # TODO: make payment a generic model
#     class Config:
#         arbitrary_types_allowed = True
#         populate_by_name = True
#         json_encoders = {ObjectId: str}


class HorseShoeingBooking(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    user_id: str
    horse_shoeing_service_id: str
    trainer_id: str
    selected_date: datetime
    pricing_option: dict
    number_of_visitors: int

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
