from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, computed_field, field_serializer

from models.logistics_company_services.enums.service_enums import ServiceAvailability
from utils.date_time import get_current_utc_datetime


class AddClubToClubService(BaseModel):
    logistics_company_id: str
    user_id: str


class ResponseAddClubToClubService(BaseModel):
    service_id: str


class UpdateClubToClubService(BaseModel):
    is_available: ServiceAvailability

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()


class ResponseGetClubToClubService(BaseModel):
    service_id: str
    logistics_company_id: str
    trucks: Optional[List]
    created_at: datetime
    updated_at: datetime
    is_available: ServiceAvailability

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value
