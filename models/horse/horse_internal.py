from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
# from data.db import PyObjectId


class InternalHorse(BaseModel):
    id: Optional[str] = Field(default_factory=lambda:
                              str(ObjectId()), alias="_id")
    # id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    year: int
    height_cm: int
    club_name: Optional[str]
    price_sar: int
    image_url: str
    contact_seller_url: str
    go_transport_url: str
