from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime

from .enums import ServiceAvailability


class Provider(BaseModel):
    provider_id: str
    provider_type: str  # later would be a user.enums.Enum


class BaseLogisticsServiceInternal(BaseModel):
    provider: Provider
    trucks: Optional[List[PyObjectId]] = []
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    is_available: ServiceAvailability
    trucks: Optional[List[str]]
    description: str
    features: str
    images: Optional[List[str]] = []

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value


class ClubToClubServiceInternal(BaseLogisticsServiceInternal): ...


class ClubToClubServiceInternalWithID(BaseLogisticsServiceInternal):
    service_id: PyObjectId = Field(None, alias="_id")


class UserTransferServiceInternal(BaseLogisticsServiceInternal): ...


class UserTransferServiceInternalWithID(BaseLogisticsServiceInternal):
    service_id: PyObjectId = Field(None, alias="_id")


class LuggageTransferServiceInternal(BaseLogisticsServiceInternal): ...


class LuggageTransferServiceInternalWithID(BaseLogisticsServiceInternal):
    service_id: PyObjectId = Field(None, alias="_id")
