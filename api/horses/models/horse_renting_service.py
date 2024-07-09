from datetime import datetime
from typing import Optional

from pydantic import BaseModel, computed_field

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
