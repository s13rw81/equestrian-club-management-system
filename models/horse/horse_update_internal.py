from pydantic import BaseModel
from typing import Optional


class InternalUpdateHorse(BaseModel):
    name: Optional[str]
    description: Optional[str]
    year: Optional[int]
    height_cm: Optional[int]
    club_name: Optional[str]
    price_sar: Optional[int]
    image_url: Optional[str]
    contact_seller_url: Optional[str]
    go_transport_url: Optional[str]
