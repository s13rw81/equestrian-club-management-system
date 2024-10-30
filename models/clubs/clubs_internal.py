from pydantic import BaseModel, field_serializer
from ..common_base import CommonBase
from ..location.location_internal import LocationInternal
from .enums.verification_status import VerificationStatus
from typing import Optional


class ClubUser(BaseModel):
    user_id: str


class IndividualService(BaseModel):
    name: str
    description: str
    trainers: list[str]


class GroupService(BaseModel):
    name: str
    description: str
    trainers: list[str]


class ClubInternal(CommonBase):
    # user-fields
    name: str
    owner_name: str
    phone_number: str
    email_id: str
    commercial_registration: str
    club_id: str
    iban: str
    description: str
    location: LocationInternal
    about: Optional[str] = None
    # system-fields
    platform_id: str
    logo: Optional[str] = None
    images: Optional[list[str]] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    users: list[ClubUser]

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        return verification_status.value
