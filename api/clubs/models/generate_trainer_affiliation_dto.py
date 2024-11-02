from pydantic import (
    BaseModel,
    constr,
    EmailStr,
    field_validator
)
import phonenumbers
from logging_config import log
from data.dbapis.trainer_affiliation import find_trainer_affiliation

class GenerateTrainerAffiliationDTO(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    email_address: EmailStr
    phone_number: str

    @field_validator("full_name")
    def full_name_capitalize(cls, full_name):
        return " ".join([item.capitalize() for item in full_name.split()])

    @field_validator("email_address")
    def email_address_validator(cls, email):

        if not email:
            return email

        result = find_trainer_affiliation(email_address=email)

        if result:
            log.info("a trainer_affiliation with the same email_address already exists, raising ValueError")
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

        result = find_trainer_affiliation(phone_number=formatted_phone_number)

        if result:
            log.info("a trainer_affiliation with the same phone_number already exists, raising ValueError")
            raise ValueError("phone_number already exists...")

        return formatted_phone_number