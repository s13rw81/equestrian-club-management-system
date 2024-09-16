from functools import lru_cache
from pydantic import BaseModel, field_serializer
from models.ratings.club_ratings_internal import ClubRatingsInternal
from ..common_base.common_base import CommonBase
from ..location.location_internal import LocationInternal
from .enums.verification_status import VerificationStatus
from typing import Optional



class ClubUser(BaseModel):
    user_id: str

class ClubInternal(CommonBase):
    # user-fields
    name: Optional[str] = None
    owner_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_id: Optional[str] = None
    commercial_registration: Optional[str] = None
    club_id: Optional[str] = None
    iban: Optional[str] = None
    description: Optional[str] = None
    location: Optional[LocationInternal] = None
    # system-fields
    platform_id: Optional[str] = None
    logo: Optional[str] = None
    images: Optional[list[str]] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    users: Optional[list[ClubUser]] = None

    @field_serializer("verification_status")
    def verification_status_serializer(self, verification_status):
        return verification_status.value








@lru_cache(maxsize=64)
def calculate_average_rating(club_id: str):
    # TODO: review this logic
    # TODO: can anonymous user add rating ?
    # TODO: can non subscribing user add rating ?

    # TODO: move this to logic then dbapi
    ratings_cursor = ClubRatingsInternal.find({"club_id": club_id})
    total = 0
    count = 0
    for rating in ratings_cursor:
        total += rating['rating']
        count += 1
    if count > 0:
        return total / count
    else:
        return None
