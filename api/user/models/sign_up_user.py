from pydantic import (
    BaseModel,
    field_validator,
    Field,
    constr,
    EmailStr
)
from typing import Optional
from models.user.enums import (
    RidingStage,
    HorseOwnership,
    EquestrianDiscipline,
    Gender,
    UserCategory
)
from validators.user import whether_user_exists
import phonenumbers
from logging_config import log


class SignUpUser(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    email_address: Optional[EmailStr] = None
    phone_number: str
    phone_otp: constr(min_length=6, max_length=6)
    password: constr(strip_whitespace=True, min_length=6) = Field(exclude=True)
    gender: Optional[Gender] = None
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None
    user_category: Optional[UserCategory] = None

    @field_validator("full_name")
    def full_name_capitalize(cls, full_name):
        return " ".join([item.capitalize() for item in full_name.split()])

    @field_validator("email_address")
    def email_address_validator(cls, email):

        if not email:
            return email

        result = whether_user_exists(email=email)

        if result:
            log.info("an user with the same email_address already exists, raising ValueError")
            raise ValueError(f"email already exists (email={email})")

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

        formatted_phone_number = phonenumbers.format_number(
            parsed_phone_number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        result = whether_user_exists(phone=formatted_phone_number)

        if result:
            log.info("an user with the same phone_number already exists, raising ValueError")
            raise ValueError("phone_number already exists...")

        return formatted_phone_number
