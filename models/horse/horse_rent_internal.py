from pydantic import BaseModel
from typing import Optional

class Horse(BaseModel):
    name: str
    description: str
    year: int
    height: int
    club: Optional[str]
    price: int
    image_url: str
    contact_option: bool
    for_sell: bool
    for_rent: bool
