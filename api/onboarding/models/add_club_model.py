from typing import List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    lat: str
    long: str


class HorseShoeingServicePricingOption(BaseModel):
    price: int
    number_of_horses: int


class RidingLessonServicePricingOption(BaseModel):
    price: int
    number_of_lessons: int


class RidingLessonService(BaseModel):
    pricing_options: List[RidingLessonServicePricingOption]


class HorseShoeingService(BaseModel):
    pricing_options: List[HorseShoeingServicePricingOption]


class GenericActivityService(BaseModel):
    price: int


class CreateClubRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    email_address: str
    phone_no: Optional[str] = None
    address: Optional[str] = None
    location: Optional[Location] = None
    riding_lesson_service: Optional[RidingLessonService] = None
    horse_shoeing_service: Optional[HorseShoeingService] = None
    generic_activity_service: Optional[GenericActivityService] = None
