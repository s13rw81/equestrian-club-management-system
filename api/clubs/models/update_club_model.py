from pydantic import (
    BaseModel,
    constr,
    EmailStr,
    field_serializer,
    field_validator,
    model_validator,
    Field
)
from uuid import UUID
import phonenumbers
from models.clubs.enums import VerificationStatus
from logging_config import log
from typing_extensions import Self
from data.dbapis.clubs import find_club


class LocationUpdate(BaseModel):
    lat: constr(min_length=1, max_length=200, pattern=r"^-?(?:90(\.0+)?|[0-8]?\d(\.\d+)?)[NS]?$") = None
    long: constr(min_length=1, max_length=200, pattern=r"^-?(?:180(\.0+)?|(?:1[0-7]\d|\d{1,2})(\.\d+)?)[EW]?$") = None


class UpdateClubRequest(BaseModel):
    # user-fields
    id: UUID = Field(..., description="club_id")
    name: constr(min_length=1, max_length=200) = None
    owner_name: constr(min_length=1, max_length=200) = None
    phone_number: constr(min_length=1, max_length=20) = None
    email_id: EmailStr = None
    commercial_registration: constr(min_length=1, max_length=200) = None
    club_id: constr(min_length=1, max_length=200) = None
    iban: constr(min_length=1, max_length=200) = None
    description: constr(min_length=1, max_length=1000) = None
    location: LocationUpdate = None
    # system-fields
    verification_status: VerificationStatus = None

    @field_serializer("id")
    def serialize_id(self, value):
        return str(value)

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        if not verification_status:
            return

        return verification_status.value

    @field_validator("phone_number")
    def validate_phone_number(cls, value):

        if not value:
            return

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

        log.info("phone_number validated successfully, returning...")

        return value

    @field_validator("club_id")
    def validate_club_id(cls, value):
        log.info(f"inside validate_club_id(club_id={value})")

        if not value:
            return

        if "_" in value:
            log.info("club_id has underscores ('_') in it, raising ValueError...")
            raise ValueError("club_id cannot have underscores ('_') in it...")

        log.info("club_id validated successfully, returning...")
        return value

    @model_validator(mode="after")
    def validate_constraints(self) -> Self:
        log.info("inside validate_constraints("
                 f"id={self.id}, email_id={self.email_id}, commercial_registration={self.commercial_registration},"
                 f"club_id={self.club_id})")

        club = find_club(id=str(self.id))

        if not club:
            log.info(f"the provided id is invalid (id={self.id}), raising ValueError...")
            raise ValueError(f"the provided id is invalid(id={self.id})")

        if not (self.email_id or self.commercial_registration or self.club_id):
            log.info(
                "neither email_id nor commercial_registration nor club_id is provided, hence no further validation "
                "is required... returning...")
            return self

        email_id = self.email_id if self.email_id else club.email_id
        commercial_registration = self.commercial_registration if self.commercial_registration else club.commercial_registration
        club_id = self.club_id if self.club_id else club.club_id

        club = find_club(
            email_id=email_id,
            commercial_registration=commercial_registration,
            club_id=club_id
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
