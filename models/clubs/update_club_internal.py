from pydantic import field_serializer, BaseModel
from ..common_base import CommonBase
from typing import Optional
from .enums import VerificationStatus

class UpdateLocationInternal(BaseModel):
    lat: str = None
    long: str = None

class UpdateClubInternal(CommonBase):
    # user-fields
    name: str = None
    owner_name: str = None
    phone_number: str = None
    email_id: str = None
    commercial_registration: str = None
    club_id: str = None
    iban: str = None
    description: str = None
    location: UpdateLocationInternal = None
    # system-fields
    platform_id: str = None
    logo: Optional[str] = None
    images: Optional[list[str]] = None
    verification_status: VerificationStatus = None

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        if not verification_status:
            return

        return verification_status.value
