import re
from datetime import datetime
from functools import lru_cache
from typing import List, Optional

from bson import ObjectId
from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from models.ratings.club_ratings_internal import ClubRatingsInternal
from models.user import StrObjectId
from models.user.user_external import UserExternal
from pydantic import BaseModel, Field, field_validator


class ClubInternal(BaseModel):
    # id: Optional[StrObjectId] = Field(alias = '_id')
    name: str = Field(..., min_length = 1)
    description: Optional[str] = Field(None, max_length = 500)
    price: Optional[float] = Field(..., gt = 0)
    address: Optional[Address] = None
    contact: Optional[Contact] = None
    creation_date_time: Optional[datetime] = None
    update_date_time: Optional[datetime] = None
    image_urls: Optional[List[str]] = None
    admins: Optional[List[UserExternal]] = list()

    # class Config:
    #     populate_by_name = True
    #     json_encoders = {ObjectId: str}
    #     arbitrary_types_allowed = True

    @field_validator('name')
    def validate_name(cls, v):
        pattern = r'^[A-Za-z0-9.\- ]+$'
        if not re.match(pattern, v):
            raise ValueError("Name can only contain alphabets, dots, and dashes")
        return v.lower()

    # @field_validator('location')
    # def validate_location(cls, v):
    #     coords = v
    #     if not isinstance(coords, dict) or len(coords) != 2:
    #         raise ValueError('location must be a dictionary with two keys: "lon" and "lat"')
    #     lon, lat = coords.get('lon'), coords.get('lat')
    #     if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
    #         raise ValueError('location must be valid longitude and latitude. longitude must be between +/-180 and latitide must be between +/- 90')
    #     return v

    @property
    def rating(self):
        return calculate_average_rating(self._id)


@lru_cache(maxsize = 64)
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
