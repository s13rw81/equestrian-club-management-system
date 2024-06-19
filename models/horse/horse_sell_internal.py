from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional


class InternalSellHorse(BaseModel):
    id: Optional[str] = Field(default_factory=lambda:
                              str(ObjectId()), alias="_id")
    name: str
    type: str
    description: str
    year: int
    height_cm: int
    club_name: Optional[str]
    price_sar: int
    image_url: str
