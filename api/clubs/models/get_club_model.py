from pydantic import BaseModel, field_serializer
from typing import Optional
from models.clubs.enums import VerificationStatus
from uuid import UUID

class GetLocation(BaseModel):
    lat: str
    long: str

class GetClub(BaseModel):
    id: UUID
    name: str
    owner_name: str
    phone_number: str
    email_id: str
    commercial_registration: str
    club_id: str
    iban: str
    location: GetLocation
    platform_id: str
    logo: Optional[str] = None
    images: Optional[list[str]] = None
    verification_status: VerificationStatus
    approx_price: Optional[str] = None
    average_rating: Optional[str] = None

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        return verification_status.value

    @field_serializer("id")
    def serialize_uuids(self, value):
        if not value:
            return

        return str(value)
