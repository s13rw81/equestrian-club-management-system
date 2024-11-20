from pydantic import (
    BaseModel,
    constr,
    EmailStr,
    field_validator,
    model_validator
)
import phonenumbers
from logging_config import log
from data.dbapis.trainer_affiliation import find_trainer_affiliation
from data.dbapis.clubs import find_club
from typing_extensions import Self

class GenerateTrainerAffiliationDTO(BaseModel):
    club_id: str
    full_name: constr(min_length=1, max_length=200)
    email_address: EmailStr
    phone_number: str

    @field_validator("club_id")
    def validate_club_id(cls, club_id):
        result = find_club(id=club_id)

        if not result:
            log.info(f"invalid club_id(club_id={club_id})")
            raise ValueError(f"invalid club_id(club_id={club_id})")

        return club_id

    @field_validator("full_name")
    def full_name_capitalize(cls, full_name):
        return " ".join([item.capitalize() for item in full_name.split()])


    @model_validator(mode="after")
    def model_validator(self) -> Self:

        if not self.phone_number or not self.club_id:
            return self

        phone_number = self.phone_number
        club_id = self.club_id

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

        result = find_trainer_affiliation(
            phone_number=formatted_phone_number,
            club_id=club_id
        )

        if result:
            log.info("a trainer_affiliation with the same phone_number and same club "
                     "already exists, raising ValueError")
            raise ValueError("a club cannot generate an affiliation number with the same phone_number "
                             "more than once")

        self.phone_number = formatted_phone_number

        return self
