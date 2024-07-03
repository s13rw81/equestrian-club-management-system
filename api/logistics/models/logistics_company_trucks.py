from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from data.db import PyObjectId
from models.truck import TruckInternal
from models.truck.enums.availability import TruckAvailability
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
    availability: TruckAvailability

    @field_serializer("availability")
    def enum_serializer(self, enum):
        return enum.value
