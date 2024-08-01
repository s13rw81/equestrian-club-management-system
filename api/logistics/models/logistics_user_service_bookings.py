from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from models.logistics_user_service_bookings.logistics_user_service_bookings import (
    Groomer,
    Location,
)
from utils.date_time import get_current_utc_datetime


class CreateBooking(BaseModel):
    truck_id: str
    pickup: Location
    destination: Location
    groomer: Groomer
    details: str = Field(min_length=1)


class ResponseCreateBooking(BaseModel):
    logistic_service_booking: str


class UpdateBooking(BaseModel):
    truck_id: Optional[str] = Field(default=None, min_length=1)
    pickup: Optional[Location] = None
    destination: Optional[Location] = None
    groomer: Optional[Groomer] = None
    details: Optional[str] = Field(default=None, min_length=1)

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()
