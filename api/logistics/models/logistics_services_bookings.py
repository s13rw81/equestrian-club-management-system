from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from data.db import PyObjectId
from models.logistics_company_services.enums import ServiceAvailability
from models.logistics_company_services.logistics_company_services import Provider
from models.logistics_service_bookings.enums import BookingStatus
from models.logistics_service_bookings.logistics_service_bookings import Location
from utils.date_time import get_current_utc_datetime


class ResponseClubToClubServices(BaseModel):
    service_id: PyObjectId = Field(None, alias="_id")
    provider: Provider
    created_at: datetime
    updated_at: datetime
    is_available: ServiceAvailability

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value


class ClubToClubServiceBooking(BaseModel):
    booking_id: PyObjectId = Field(None, alias="_id")
    service_id: str
    consumer_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    truck_id: str
    pickup_time: str
    destination_location: Location
    source_location: Location

    @computed_field
    @property
    def current_location(self) -> str:
        """while creating the booking the source location is the current location"""
        return self.source_location

    @field_validator("pickup_time")
    @classmethod
    def parse_date(cls, pickup_time: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(pickup_time)
        except ValueError:
            raise ValueError("Incorrect date format provided.")


class ResponseClubToClubServiceBooking(BaseModel):
    booking_id: str
    booking_status: BookingStatus
    message: str

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        return enum.value


class UpdateClubToClubServiceBooking(BaseModel):
    horse_id: str = None
    pickup_time: str = None
    source_club_id: str = None
    destination_club_id: str = None
    source_location: Location = None
    destination_location: Location = None
    booking_status: BookingStatus = None

    @field_validator("pickup_time")
    @classmethod
    def parse_date(cls, pickup_time: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(pickup_time)
        except ValueError:
            raise ValueError("Incorrect date format provided.")

    @computed_field
    def current_location(self) -> Location:
        return self.source_location

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()

    @model_validator(mode="after")
    def validate_location(self):
        if (self.source_club_id and not self.source_location) or (
            self.source_location and not self.source_club_id
        ):
            raise ValueError("Source club and source club location both are required")

        if (self.destination_club_id and not self.destination_location) or (
            self.destination_location and not self.destination_club_id
        ):
            raise ValueError(
                "Destination club and destincation club location both are required"
            )

        if self.pickup_time and self.pickup_time <= datetime.now():
            raise ValueError("pickup time should be a future time")

        return self

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        return enum.value
