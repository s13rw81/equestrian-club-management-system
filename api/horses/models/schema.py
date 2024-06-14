from pydantic import BaseModel, Field
from typing import Optional

class HorseBase(BaseModel):
    name: str = Field(..., example="Thunderbolt")
    description: str = Field(..., example="A fast and reliable horse.")
    year: int = Field(..., example=2015)
    height_cm: int = Field(..., example=160)
    club_name: Optional[str] = Field(None, example="Sunset Riders Club")
    price_sar: int = Field(..., example=50000)
    image_url: str = Field(..., example="http://example.com/image.jpg")
    contact_seller_url: str = Field(..., example="http://example.com/contact")
    go_transport_url: str = Field(..., example="http://example.com/transport")

class HorseCreate(HorseBase):
    pass

class HorseUpdate(HorseBase):
    pass

class HorseInDBBase(HorseBase):
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        orm_mode = True

class Horse(HorseInDBBase):
    pass

class HorseInDB(HorseInDBBase):
    pass
