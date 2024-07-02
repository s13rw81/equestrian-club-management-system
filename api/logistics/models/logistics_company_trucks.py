import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from data.db import PyObjectId
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


class ViewTruck(BaseModel):
    truck_id: PyObjectId = Field(None, alias="_id")
    name: str
    availability: str
    capacity: int
    logistics_company_id: str
    registration_number: str


class ResponseViewTruck(BaseModel):
    truck_id: str
    name: str
    availability: str
    capacity: int
    logistics_company_id: str
    registration_number: str


class TruckImages(BaseModel):
    image_key: str
    description: str = Field(max_length=200)


class TruckDetails(BaseModel):
    truck_id: PyObjectId = Field(alias="_id")
    name: str
    truck_type: str
    availability: str
    images: List[TruckImages]
    logistics_company_id: str
    registration_number: str


class ResponseTruckDetails(BaseModel):
    truck_id: str
    name: str
    truck_type: str
    availability: str
    images: List[TruckImages]
    logistics_company_id: str
    registration_number: str


class UpdateTruckDetails(BaseModel):
    availability: TruckAvailability

    @field_serializer("availability")
    def enum_serializer(self, enum):
        return enum.value


class UploadTruckImages(BaseModel):
    description: List[str]

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
