import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, model_validator

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


class UpdateAvailability(BaseModel):
    availability_id: str
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


class UpdateClubServiceRequest(BaseModel):
    service_type: Optional[ServiceType] = None
    sub_service: Optional[SubServices] = None
    service_status: Optional[ServiceStatus] = None
    services: Optional[list[str]] = None
    capacity: Optional[int] = None
    no_of_services: Optional[int] = None
    commision: Optional[float] = None
    pricing: Optional[str] = None
    discount: Optional[float] = None
    availability: Optional[list[UpdateAvailability]] = None

    @model_validator(mode="after")
    def validate_sub_service(self):
        if self.capacity and self.sub_service != SubServices.GROUP:
            logging.error(
                "capacity provided but sub_service is not a group. raising error"
            )
            ValueError(f"capacity provided for {self.sub_service} sub service")

        if self.sub_service == SubServices.GROUP:
            if not self.capacity:
                logging.error(
                    "capacity not provided for group sub service. raising error"
                )
                ValueError("capacity not provided for group sub service")

        return self


class ResponseAvailability(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime


class ResponseGetClubService(BaseModel):
    id: str
    service_type: ServiceType
    sub_service: SubServices
    service_status: ServiceStatus
    services: list[str]
    capacity: Optional[int] = None
    no_of_services: int
    commision: float
    pricing: str
    discount: float
    availability: list[ResponseAvailability]

    @field_serializer("service_type")
    def serialize_service_type(self, value):
        return value.name if value else None

    @field_serializer("sub_service")
    def serialize_sub_service(self, value):
        return value.name if value else None

    @field_serializer("service_status")
    def serialize_service_status(self, value):
        return value.name if value else None
