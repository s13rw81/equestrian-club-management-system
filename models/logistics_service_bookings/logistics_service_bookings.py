from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer
from pydantic_extra_types.coordinate import Latitude, Longitude

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime

from .enums import BookingStatus


class Location(BaseModel):
    latitude: Latitude
    longitude: Longitude


class Consumer(BaseModel):
    consumer_id: str
    consumer_type: str = "CLUB"


# this is for transfer of horses between clubs
class ClubToClubServiceBookingInternal(BaseModel):
    booking_id: PyObjectId = Field(None, alias="_id")
    consumer: Consumer
    service_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    source_location: Location
    destination_location: Location
    current_location: Location
    truck_id: str
    pickup_time: datetime
    booking_status: BookingStatus
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
