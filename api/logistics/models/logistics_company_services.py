from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, computed_field, field_serializer

from models.logistics_company_services.enums.service_enums import ServiceAvailability
from utils.date_time import get_current_utc_datetime


class AddBaseLogisticsService(BaseModel):
    trucks: List[str]
    features: str
    description: str


class ResponseBaseAddLogisticsService(BaseModel):
    logistic_service_club_to_club_id: str


class ResponseBaseGetLogisticsService(BaseModel):
    service_id: str
    logistics_company_id: str
    trucks: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    is_available: ServiceAvailability
    features: str
    description: str
    images: Optional[List[str]]

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value


class UpdateBaseLogisticsService(BaseModel):
    is_available: ServiceAvailability

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()


class AddClubToClubService(AddBaseLogisticsService): ...


class ResponseAddClubToClubService(ResponseBaseAddLogisticsService): ...


class AddUserTransferService(AddBaseLogisticsService): ...


class ResponseAddUserTransferService(ResponseBaseAddLogisticsService): ...


class AddLuggageTransferService(AddBaseLogisticsService): ...


class ResponseAddLuggageTransferService(ResponseBaseAddLogisticsService): ...


class ResponseGetClubToClubService(ResponseBaseGetLogisticsService): ...


class ResponseGetUserTransferService(ResponseBaseGetLogisticsService): ...


class ResponseGetLuggageTransferService(ResponseBaseGetLogisticsService): ...


class UpdateClubToClubService(UpdateBaseLogisticsService): ...


class UpdateUserTransferService(UpdateBaseLogisticsService): ...


class UpdateLuggageTransferService(UpdateBaseLogisticsService): ...
