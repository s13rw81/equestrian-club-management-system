from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

from data.db import PyObjectId
from models.truck import TruckInternal
from models.truck.enums.availability import TruckAvailability
from utils.date_time import get_current_utc_datetime
from utils.logistics_utils import LogisticsService


class AddTruck(BaseModel):
    registration_number: str
    truck_type: str
    capacity: int
    special_features: str = Field(max_length=200)
    gps_equipped: bool
    air_conditioning: bool
    name: str
    services: List[LogisticsService]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("services")
    def enum_serializer(self, services):
        return [service.value for service in services]


class AddTruckResponse(BaseModel):
    truck_id: str


class ViewTruck(TruckInternal):
    truck_id: PyObjectId = Field(None, alias="_id")


class ResponseViewTruck(TruckInternal):
    truck_id: str


class TruckDetails(TruckInternal):
    truck_id: PyObjectId = Field(alias="_id")


class ResponseTruckDetails(TruckInternal):
    truck_id: str


class UpdateTruckDetails(BaseModel):
    availability: Optional[TruckAvailability] = None
    registration_number: Optional[str] = None
    truck_type: Optional[str] = None
    capacity: Optional[str] = None
    special_features: Optional[str] = None
    gps_equipped: Optional[str] = None
    air_conditioning: Optional[str] = None
    name: Optional[str] = None

    @field_serializer("availability")
    def enum_serializer(self, enum):
        return enum.value

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()
