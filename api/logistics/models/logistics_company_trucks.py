from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

from data.db import PyObjectId
from models.truck import Driver, Location, TruckInternal
from models.truck.enums.availability import TruckAvailability
from utils.date_time import get_current_utc_datetime

# from utils.logistics_utils import LogisticsService


class AddTruck(BaseModel):
    registration_number: str = Field(min_length=1)
    truck_type: str = Field(min_length=1)
    capacity: str
    special_features: str = Field(min_length=1, max_length=200)
    gps_equipped: bool
    air_conditioning: bool
    name: str = Field(min_length=1)
    driver: Driver
    location: Location
    # services: List[LogisticsService]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # @field_serializer("services")
    # def enum_serializer(self, services):
    #     return [service.value for service in services]


class AddTruckResponse(BaseModel):
    truck_id: str


class BaseTruckResponseFields(BaseModel):
    logistics_company_id: str
    registration_number: str
    truck_type: str
    capacity: str
    special_features: str
    gps_equipped: bool
    air_conditioning: bool
    name: str
    truck_id: str
    image_urls: List[str]
    driver: Driver
    location: Location


class ViewTruck(BaseTruckResponseFields):
    truck_id: PyObjectId = Field(None, alias="_id")
    image_urls: List[str] = Field(alias="images")


class ResponseViewTruck(BaseTruckResponseFields):
    truck_id: str


class TruckDetails(TruckInternal):
    truck_id: PyObjectId = Field(alias="_id")
    image_urls: List[str] = Field(alias="images")


class ResponseTruckDetails(BaseTruckResponseFields):
    truck_id: str


class UpdateTruckDetails(BaseModel):
    # availability: Optional[TruckAvailability] = Field(default=None, min_length=1)
    registration_number: Optional[str] = Field(default=None, min_length=1)
    truck_type: Optional[str] = Field(default=None, min_length=1)
    capacity: Optional[str] = Field(default=None)
    special_features: Optional[str] = Field(default=None, min_length=1)
    gps_equipped: Optional[bool] = None
    air_conditioning: Optional[bool] = None
    name: Optional[str] = Field(default=None, min_length=1)
    location: Optional[Location] = None
    driver: Optional[Driver] = None

    # @field_serializer("availability")
    # def enum_serializer(self, enum):
    #     return enum.value

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()
