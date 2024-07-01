from datetime import datetime
from typing import List, Optional

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
from models.logistics_service_bookings import (
    ClubToClubServiceBookingInternal,
    Consumer,
    Groomer,
    Horse,
    ItemsToMove,
    Location,
    LuggageTransferServiceBookingInternal,
    UserTransferServiceBookingInternal,
)
from models.logistics_service_bookings.enums import BookingStatus
from utils.date_time import get_current_utc_datetime


class BaseLogisticsServices(BaseModel):
    service_id: PyObjectId = Field(None, alias="_id")
    provider: Provider
    created_at: datetime
    updated_at: datetime
    is_available: ServiceAvailability

    @field_serializer("is_available")
    def enum_serializer(self, enum):
        return enum.value

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class ResponseBaseLogisticsServices(BaseModel):
    service_id: str
    provider: Provider
    created_at: datetime
    updated_at: datetime
    is_available: ServiceAvailability


class ClubToClubServices(BaseLogisticsServices): ...


class ResponseClubToClubServices(ResponseBaseLogisticsServices): ...


class BookClubToClubService(BaseModel):
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


class ResponseBookClubToClubServiceBooking(BaseModel):
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
        if not enum:
            return
        return enum.value


class ClubToClubServiceBooking(ClubToClubServiceBookingInternal):
    booking_id: PyObjectId = Field(None, alias="_id")


class ResponseClubToClubServiceBooking(BaseModel):
    booking_id: str
    consumer: Consumer
    service_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    source_location: Location
    destination_location: Location
    current_location: Location
    truck_id: str
    pickup_time: datetime
    booking_status: BookingStatus
    created_at: datetime
    updated_at: datetime


class UserTransferServices(BaseLogisticsServices): ...


class ResponseUserTransferServices(ResponseBaseLogisticsServices): ...


class BookUserTransferService(BaseModel):
    logistics_company_id: str
    truck_id: str
    destination_location: Location
    source_location: Location
    pickup_time: str
    horse_info: Horse
    groomer_info: Groomer

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


class ResponseBookUserTransferService(BaseModel):
    booking_id: str
    booking_status: BookingStatus
    message: str

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        return enum.value


class UpdateUserTransferServiceBooking(BaseModel):
    pickup_time: str = None
    source_location: Location = None
    destination_location: Location = None
    booking_status: BookingStatus = None
    horse_info: Horse = None
    groomer_info: Groomer = None

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
        if self.pickup_time and self.pickup_time <= datetime.now():
            raise ValueError("pickup time should be a future time")

        return self

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        if not enum:
            return
        return enum.value


class ResponseUserTransferServiceBooking(BaseModel):
    booking_id: str
    consumer: Consumer
    service_id: str
    logistics_company_id: str
    truck_id: str
    source_location: Location
    destination_location: Location
    current_location: Location
    pickup_time: datetime
    booking_status: BookingStatus
    horse_info: Horse
    groomer_info: Groomer
    created_at: datetime
    updated_at: datetime


class UserTransferServiceBooking(UserTransferServiceBookingInternal):
    booking_id: PyObjectId = Field(None, alias="_id")


class LuggageTransferService(BaseLogisticsServices): ...


class ResponseLuggageTransferService(ResponseBaseLogisticsServices): ...


class BookLuggageTransferService(BaseModel):
    destination_location: Location
    source_location: Location
    logistics_company_id: str
    truck_id: str
    pickup_time: str
    dedicated_labour: bool
    items_to_move: List[ItemsToMove]

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


class ResponseBookLuggageTransferService(BaseModel):
    booking_id: str
    booking_status: BookingStatus
    message: str

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        return enum.value


class UpdateLuggageTransferServiceBooking(BaseModel):
    pickup_time: str = None
    source_location: Location = None
    destination_location: Location = None
    booking_status: BookingStatus = None
    dedicated_labour: bool = None

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
        if self.pickup_time and self.pickup_time <= datetime.now():
            raise ValueError("pickup time should be a future time")

        return self

    @field_serializer("booking_status")
    def enum_serializer(self, enum):
        if not enum:
            return
        return enum.value


class ResponseLuggageTransferServiceBooking(BaseModel):
    booking_id: str
    consumer: Consumer
    service_id: str
    logistics_company_id: str
    truck_id: str
    source_location: Location
    destination_location: Location
    current_location: Location
    pickup_time: datetime
    booking_status: BookingStatus
    items_to_move: List[ItemsToMove]
    dedicated_labour: bool
    created_at: datetime
    updated_at: datetime


class LuggageTransferServiceBooking(LuggageTransferServiceBookingInternal):
    booking_id: PyObjectId = Field(None, alias="_id")
