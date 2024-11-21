from pydantic import BaseModel, field_serializer, field_validator
from typing import Optional
from models.clubs.enums import VerificationStatus
from uuid import UUID
from utils.image_management import generate_image_url, generate_image_urls


class GetLocation(BaseModel):
    lat: str
    long: str


class GetClubDTO(BaseModel):
    id: UUID
    name: str
    owner_name: str
    phone_number: str
    email_id: str
    commercial_registration: str
    club_id: str
    iban: str
    description: str
    location: GetLocation
    about: Optional[str] = None
    platform_id: str
    logo: Optional[str] = None
    images: Optional[list[str]] = None
    verification_status: VerificationStatus
    approx_price: Optional[str] = None
    average_rating: Optional[str] = None

    @field_validator("logo")
    def convert_image_id_to_url(cls, logo):
        if not logo:
            return logo

        # if the logo is a valid UUID, only then it needs to be converted
        # to an image url, otherwise, it can be safely assumed that the UUID has
        # already been converted to a URL and no further intervention is required
        try:
            UUID(logo)
        except:
            return logo

        return generate_image_url(image_id=logo)

    @field_validator("images")
    def convert_image_id_to_urls(cls, images):
        if not images:
            return

        # if the first element of the list is a valid UUID, only then all the elements need
        # to be converted to image urls, otherwise, it can be safely assumed that the UUIDs have
        # already been converted to URLs and no further intervention is required
        try:
            UUID(images[0])
        except:
            return images

        return generate_image_urls(image_ids=images)

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        return verification_status.value

    @field_serializer("id")
    def serialize_uuids(self, value):
        if not value:
            return

        return str(value)
