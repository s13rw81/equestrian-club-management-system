import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from ..common_base import CommonBase


class AvailabilityInternal(CommonBase):
    club_service_id: str
    start_time: datetime
    end_time: datetime


class ClubServiceInternal(CommonBase):
    club_id: str
    capacity: Optional[int] = None
    service_type: str
    sub_service: str
    services: list[str]
    service_status: str
    no_of_services: int
    # availability: list[Availability]
    currency: str = "SAR"
    commision: float = 5.0
    pricing: str
    discount: float


class UpdateAvailabilityInternal(CommonBase):
    club_service_id: str
    availability_id: str
    start_time: datetime
    end_time: datetime


class UpdateClubServiceInternal(CommonBase):
    capacity: Optional[int] = None
    service_type: Optional[str] = None
    sub_service: Optional[str] = None
    service_status: Optional[str] = None
    services: Optional[list[str]] = None
    no_of_services: Optional[int] = None
    currency: Optional[str] = None
    commision: Optional[float] = None
    pricing: Optional[str] = None
    discount: Optional[str] = None
