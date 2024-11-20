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
