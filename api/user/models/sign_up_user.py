from pydantic import (
    BaseModel,
    field_validator,
    Field,
    constr,
    EmailStr
)
from typing import Optional
from models.user.enums import RidingStage, HorseOwnership, EquestrianDiscipline
from validators.user import whether_user_exists
import phonenumbers
from logging_config import log


class SignUpUser(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    email_address: EmailStr
    phone_number: str
    phone_otp: constr(min_length=6, max_length=6)
    password: str = Field(exclude=True)
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None

    @field_validator("email_address")
    def email_address_validator(cls, email):

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

    @field_validator("password")
    def password_validator(cls, password: str) -> str:
        password = password.strip()

        if len(password) < 6:
            log.info("password length is less than 6 characters, raising ValueError")
            raise ValueError("password should be more than 5 characters...")

        return password
