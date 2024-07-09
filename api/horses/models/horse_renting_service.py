from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field, field_validator, model_validator

from utils.date_time import get_current_utc_datetime


class EnlistHorseForRent(BaseModel):
    name: str
    year_of_birth: str
    breed: str
    size: str
    gender: str
    description: str
    price: str


class EnlistHorseForRentResponse(BaseModel):
    horse_renting_service_id: str


class UpdateHorseForRentServiceListing(BaseModel):

    name: Optional[str] = None
    year_of_birth: Optional[str] = None
    breed: Optional[str] = None
    size: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()


class HorseRentEnquiry(BaseModel):
    horse_renting_service_id: str
    message: str
    date: str
    duration: int

    @field_validator("date")
    @classmethod
    def parse_date(cls, date: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(date)
        except ValueError:
            raise ValueError("Incorrect date format provided.")

    @model_validator(mode="after")
    def validate_all_fields(self):
        if self.date <= datetime.now():
            raise ValueError("date should be a future date")

        if self.duration <= 0:
            raise ValueError("duration should be a positive integer")

        return self


class CreateRentEnquiryResponse(BaseModel):
    horse_renting_enquiry_id: str
