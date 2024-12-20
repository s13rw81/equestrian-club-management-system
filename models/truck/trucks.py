from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic_extra_types.coordinate import Latitude, Longitude

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime
from utils.logistics_utils import LogisticsService

from .enums import TruckAvailability


class Location(BaseModel):
    lat: Latitude
    long: Longitude


class Driver(BaseModel):
    name: str = Field(min_length=1)
    phone_no: str = Field(min_length=10)


class TruckInternal(BaseModel):
    registration_number: str
    truck_type: str
    capacity: str
    gps_equipped: bool
    special_features: str
    air_conditioning: bool
    logistics_company_id: str
    name: str
    availability: TruckAvailability = TruckAvailability.UN_AVAILABLE.value
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    images: List[str] = []
    location: Location
    driver: Driver
    # services: List[LogisticsService]

    # @field_serializer("services")
    # def enum_serializer(self, services):
    #     return [service.value for service in services]

    model_config = ConfigDict(arbitrary_types_allowed=True)
