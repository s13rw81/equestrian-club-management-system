from pydantic import BaseModel
from typing import Optional


class InternalUpdateSellHorse(BaseModel):
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]
    year: Optional[int]
    height_cm: Optional[int]
    price_sar: Optional[int]
    image_url: Optional[str]
    uploaded_by_id: Optional[str]
    uploaded_by_type: Optional[str]
