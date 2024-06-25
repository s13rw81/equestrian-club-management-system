from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from data.db import PyObjectId
from models.logistics_company_services.enums.service_enums import ServiceType
from utils.date_time import get_current_utc_datetime

from .enums import TruckAvailability


class TruckImages(BaseModel):
    image_key: str
    description: str = Field(max_length=200)


class TruckInternal(BaseModel):
    registration_number: str
    truck_type: str
    capacity: int
    gps_equipped: bool
    special_features: str = Field(max_length=200)
    air_conditioning: bool
    logistics_company_id: Optional[PyObjectId] = Field(alias="logistics_company_id")
    name: str = ""
    availability: TruckAvailability = TruckAvailability.UN_AVAILABLE.value
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    images: List[TruckImages] = []
    services: List[ServiceType]

    @field_serializer("services")
    def enum_serializer(self, services):
        return [service.value for service in services]

    model_config = ConfigDict(arbitrary_types_allowed=True)
