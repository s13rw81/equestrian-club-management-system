import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, model_validator

from models.clubs.enums.service import ServiceStatus, ServiceType, SubServices


class Availability(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate(self):
        if self.start_time >= self.end_time:
            logging.error(
                f"start_time {self.start_time} is greater than end_time {self.end_time}"
            )
            raise ValueError("invalid start_time and end_time provided")
        return self


class AddClubServiceRequest(BaseModel):
    club_id: str
    service_type: ServiceType
    sub_service: SubServices
    service_status: ServiceStatus = Field(default=ServiceStatus.DISABLE)
    services: list[str]
    capacity: Optional[int] = None
    no_of_services: int
    commision: float = 5.0
    pricing: str
    discount: float
    availability: list[Availability]

    @model_validator(mode="after")
    def validate_sub_service(self):
        if self.sub_service == SubServices.GROUP:
            if not self.capacity:
                logging.error(
                    "capacity not provided for group sub service. raising error"
                )
                ValueError("capacity not provided for group sub service")
        return self
