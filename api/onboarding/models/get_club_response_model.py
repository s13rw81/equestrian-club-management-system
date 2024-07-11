from typing import Optional

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel, Field


class GetClubResponse(BaseModel):
    id: str
    name: str
    description: str
    email_address: str
    phone_no: str
    address: str
    is_khayyal_verified: bool
    image_urls: list


# {
#   "id": "the id of the club",
#   "email_address": "someemail@domain.com",
#   "address": "the address of the club"
#   "phone_no": "+911111111111",
#   "name": "name of the club",
#   "description": "a description of the club",
#   "is_khayyal_verified": false,
#   "image_urls": [
#     "club.images[0]",
#     "club.images[1]",
#     "club.images[3]"
#   ]
# }

