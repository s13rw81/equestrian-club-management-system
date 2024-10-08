from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from typing_extensions import Self
from logging_config import log
import phonenumbers


class GenerateSignUpOtpDTO(BaseModel):
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @field_validator("phone_number")
    def validate_phone_number(cls, value):

        if not value:
            return value

        log.info(f"validating phone number in GenerateSignUpOtpDTO(phone_number={value})")

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
    def check_whether_either_email_or_phone_provided(self) -> Self:

        email_address = self.email_address
        phone_number = self.phone_number

        if email_address and phone_number:
            log.info("email_address and phone_number cannot be present simultaneously, raising ValueError")
            raise ValueError("email_address and phone_number cannot be present simultaneously")

        if not (email_address or phone_number):
            log.info("either email_address or phone_number must be present, raising ValueError")
            raise ValueError("either email_address or phone_number must be present, raising ValueError")

        return self