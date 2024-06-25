# horses_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class HorseSellCreate(BaseModel):
    name: str = Field(..., example="Bobby")
    type: str = Field(..., example="Gelding")
    description: str = Field(..., example="A horse for the future.")
    year: int = Field(..., example=2015)
    height_cm: int = Field(..., example=160)
    price_sar: int = Field(..., example=50000)
    image_url: str = Field(..., example="http://example.com/image.jpg")
    uploaded_by_id: Optional[str] = Field(None, example="1234")
    uploaded_by_type: Optional[str] = Field(None, example="user")
