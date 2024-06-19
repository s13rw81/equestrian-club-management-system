from pydantic import BaseModel
from typing import Optional


class InternalUpdateSellHorse(BaseModel):
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]
    year: Optional[int]
    height_cm: Optional[int]
    club_name: Optional[str]
    price_sar: Optional[int]
    image_url: Optional[str]
