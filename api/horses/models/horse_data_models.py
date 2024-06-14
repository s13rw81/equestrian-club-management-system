from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4


class Horse(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    year: int
    height_cm: int
    club_name: str
    price_sar: int
    image_url: str
    contact_seller_url: str
    go_transport_url: str
