from datetime import datetime
from typing import Optional

from bson import ObjectId
from data.db import PyObjectId
from models.generic_models.generic_address_model import Address
from models.riding_lession_services.riding_lesson_service_model import RidingLessonService

from models.user.user_external import UserExternal
from pydantic import BaseModel, Field
from utils.date_time import get_current_utc_datetime


class RidingLessonBooking(BaseModel):
    id: Optional[PyObjectId] = Field(alias = '_id', default = None)
    lesson_service: RidingLessonService
    rider: UserExternal
    trainer: UserExternal
    lesson_datetime: datetime = Field(default_factory = get_current_utc_datetime)
    booking_datetime: datetime = Field(default_factory = get_current_utc_datetime)
    update_datetime: datetime = Field(default_factory = get_current_utc_datetime)
    venue: Address
    payment_status: str  # TODO: change to an ENUM
    booking_status: str  # TODO: change to an ENUM

    # TODO: make payment a generic model
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
