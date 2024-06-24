from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime

from .enums import ServiceAvailability


class Provider(BaseModel):
    provider_id: str
    provider_type: str  # later would be a user.enums.Enum


class ClubToClubServiceInternal(BaseModel):
    service_id: Optional[PyObjectId] = Field(None, alias="_id")
    provider: Provider
    trucks: Optional[List[PyObjectId]] = []
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    is_available: ServiceAvailability

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value


class UserTransferServiceInternal(BaseModel):
    provider: Provider
    trucks: Optional[List[PyObjectId]] = []
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    is_available: ServiceAvailability

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value


class UserTransferServiceWithInsuranceInternal(BaseModel):
    provider: Provider
    trucks: Optional[List[PyObjectId]] = []
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    is_available: ServiceAvailability

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value
