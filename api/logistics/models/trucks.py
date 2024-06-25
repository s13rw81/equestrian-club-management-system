from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from data.db import PyObjectId
from models.logistics_company_services.enums.service_enums import ServiceType
from models.truck.enums.availability import TruckAvailability


class AddTruck(BaseModel):
    registration_number: str
    truck_type: str
    capacity: int
    special_features: str = Field(max_length=200)
    gps_equipped: bool
    air_conditioning: bool
    logistics_company_id: Optional[PyObjectId] = Field(alias="logistics_company_id")
    name: str = ""
    services: List[ServiceType]

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("services")
    def enum_serializer(self, services):
        return [service.value for service in services]


class AddTruckResponse(BaseModel):
    success: bool
    truck_id: str
    message: str


class ViewTruckResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    availability: str
    capacity: int
    logistics_company_id: str
    registration_number: str


class TruckImages(BaseModel):
    image_key: str
    description: str = Field(max_length=200)


class ResponseTruckDetails(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    truck_type: str
    availability: str
    images: List[TruckImages]
    logistics_company_id: str
    registration_number: str


class UpdateTruckDetails(BaseModel):
    truck_id: str
    availability: TruckAvailability

    @field_serializer("availability")
    def enum_serializer(self, enum):
        return enum.value
