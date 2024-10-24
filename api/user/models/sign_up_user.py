from pydantic import (
    BaseModel,
    field_validator,
    Field,
    constr,
    EmailStr
)
from typing import Optional, List
from models.user.enums import RidingStage, HorseOwnership, EquestrianDiscipline, UserRoles
from validators.user import whether_user_exists
import phonenumbers
from logging_config import log

"""__________________________________________________________________________________________________________________"""


# model for countries
class Country(BaseModel):
    country_name: str
    country_code: str  # e.g., 'IN' for India
    country_iso: Optional[str] = None  # Optional ISO code if needed


"""__________________________________________________________________________________________________________________"""


class SignUpUser(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    email_address: Optional[EmailStr] = None
    phone_number: str
    phone_otp: constr(min_length=6, max_length=6)
    password: constr(strip_whitespace=True, min_length=6) = Field(exclude=True)
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None
    country: List[Country] = []  # List of countries available for selection
    user_category: Optional[UserRoles] = None

    @field_validator("email_address")
    def email_address_validator(cls, email):

        if not email:
            return email

        result = whether_user_exists(email=email)

        if result:
            log.info("an user with the same email_address already exists, raising ValueError")
            raise ValueError("email already exists...")

        return email

    @field_validator("phone_number")
    def phone_number_validator(cls, phone_number):

        error = ValueError(f"invalid phone number (phone_number={phone_number})")

        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            log.info(f"failed to parse phone number, raising error (phone_number={phone_number})")
            raise error

        if not phonenumbers.is_valid_number(parsed_phone_number):
            log.info(f"phone number is not valid, raising error (phone_number={phone_number})")
            raise error

        result = whether_user_exists(phone=phone_number)

        if result:
            log.info("an user with the same phone_number already exists, raising ValueError")
            raise ValueError("phone_number already exists...")

        return phonenumbers.format_number(parsed_phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
