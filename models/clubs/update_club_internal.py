from datetime import datetime
from typing import Optional, List

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from models.user.user_external import UserExternal
from pydantic import Field
from utils.date_time import get_current_utc_datetime


class UpdateClubInternal:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    address: Optional[Address] = None
    contact: Optional[Contact] = None
    updated_at: datetime = Field(default_factory = get_current_utc_datetime)
    image_urls: Optional[List[str]] = list()
    admins: Optional[List[UserExternal]] = list()
