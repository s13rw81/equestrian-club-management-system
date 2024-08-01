from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_serializer
from pydantic_extra_types.coordinate import Latitude, Longitude

from models.user import UserRoles
from utils.date_time import get_current_utc_datetime


class Location(BaseModel):
    latitude: Latitude
    longitude: Longitude


class Consumer(BaseModel):
    consumer_id: str
    consumer_type: UserRoles = UserRoles.USER

    @field_serializer("consumer_type")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value


class Groomer(BaseModel):
    name: str = Field(min_length=1)
    phone_no: str = Field(min_length=10)


class LogisticsServiceBookingInternal(BaseModel):
    logistics_company_id: str
    truck_id: str
    consumer: Consumer
    pickup: Location
    destination: Location
    groomer: Groomer
    details: str
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
