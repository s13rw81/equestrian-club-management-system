# horses_schema.py
from pydantic import BaseModel, Field
from typing import Optional


class HorseBase(BaseModel):
    pass


class HorseSellCreate(BaseModel):
    name: str = Field(..., example="Bobby")
    type: str = Field(..., example="Gelding")
    description: str = Field(..., example="A horse for the future.")
    year: int = Field(..., example=2015)
    height_cm: int = Field(..., example=160)
    club_name: Optional[str] = Field(None, example="Sunset Riders Club")
    price_sar: int = Field(..., example=50000)
    image_url: str = Field(..., example="http://example.com/image.jpg")


class HorseInDBBase(HorseBase):
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        orm_mode = True


class Horse(HorseInDBBase):
    pass


class HorseInDB(HorseInDBBase):
    pass
