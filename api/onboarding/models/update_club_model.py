from typing import Optional, List

from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel, field_validator
from validators.clubs.clubs_exists import check_club_email_exists


class UpdateClubRequest(BaseModel):
    email_address: Optional[str] = None
    phone_no: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_khayyal_verified: bool = None
    images: Optional[List[str]] = []
    users: Optional[List] = []
