from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, field_serializer

from data.db import PyObjectId
from models.user.enums.user_roles import UserRoles
from utils.date_time import get_current_utc_datetime


class Provider(BaseModel):
    provider_id: str
    provider_type: UserRoles

    @field_serializer("provider_type")
    def enum_serializer(self, enum):
        return enum.value


class HorseRentingServiceInternal(BaseModel):
    horse_id: str
    provider: Provider
    price: str
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)


class HorseRentingServiceInternalWithID(HorseRentingServiceInternal):
    service_id: Annotated[PyObjectId, str] = Field(default=None, alias="_id")


class HorseRentingServiceEnquiryInternal(BaseModel):
    user_id: str
    horse_renting_service_id: str
    message: Optional[str] = None
    date: datetime
    duration: int
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)


class HorseRentingServiceEnquiryInternalWithID(HorseRentingServiceEnquiryInternal):
    horse_renting_enquiry_id: Annotated[PyObjectId, str] = Field(
        default=None, alias="_id"
    )
