from pydantic import BaseModel, Field
from typing import Optional


class HorseSellUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Bobby")
    type: Optional[str] = Field(None, example="Gelding")
    description: Optional[str] = Field(None, example="""Bobby is well-behaved and has excellent ring qualities.""")
    year: Optional[int] = Field(None, example=2017)
    height_cm: Optional[int] = Field(None, example=170)
    price_sar: Optional[int] = Field(None, example=75000)
    image_url: Optional[str] = Field(None, example="http://example.com/image.jpg")
    uploaded_by_id: Optional[str] = Field(None, example="1234")
    uploaded_by_type: Optional[str] = Field(None, example="user")

