from typing import List
from pydantic import BaseModel, EmailStr, constr, field_validator, model_validator
from data.dbapis.clubs import find_club
from typing_extensions import Self
import phonenumbers
from logging_config import log


class LocationIn(BaseModel):
    lat: constr(min_length=1, max_length=200, pattern=r"^-?(?:90(\.0+)?|[0-8]?\d(\.\d+)?)[NS]?$")
    long: constr(min_length=1, max_length=200, pattern=r"^-?(?:180(\.0+)?|(?:1[0-7]\d|\d{1,2})(\.\d+)?)[EW]?$")


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
    name: constr(min_length=1, max_length=200)
    owner_name: constr(min_length=1, max_length=200)
    phone_number: constr(min_length=1, max_length=20)
    email_id: EmailStr
    commercial_registration: constr(min_length=1, max_length=200)
    club_id: constr(min_length=1, max_length=200)
    iban: constr(min_length=1, max_length=200)
    description: constr(min_length=1, max_length=1000)
    location: LocationIn

    @field_validator("phone_number")
    def validate_phone_number(cls, value):

        log.info(f"validating phone number in CreateClubRequest(phone_number={value})")

        error = ValueError(f"invalid phone number (phone_number={value})")

        try:
            parsed_phone_number = phonenumbers.parse(value)
        except phonenumbers.NumberParseException:
            log.info(f"failed to parse phone number, raising error (phone_number={value})")
            raise error

        if not phonenumbers.is_valid_number(parsed_phone_number):
            log.info(f"phone number is not valid, raising error (phone_number={value})")
            raise error

        return value

    @model_validator(mode="after")
    def check_whether_club_already_exists(self) -> Self:
        log.info("inside validator check_whether_club_already_exists()")
        club = find_club(
            email_id=self.email_id,
            commercial_registration=self.commercial_registration,
            club_id=self.club_id
        )

        if club:
            log.info("club already exists with the provided data, raising error("
                     f"email_id={self.email_id}, commercial_registration={self.commercial_registration},"
                     f"club_id={self.club_id})")
            raise ValueError(
                f"club already exists with the provided data (email_id={self.email_id}, "
                f"commercial_registration={self.commercial_registration}, club_id={self.club_id})"
            )

        log.info("validation successfully completed, no club exists with the provided data...")
        return self
