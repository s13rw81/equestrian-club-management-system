from pydantic import BaseModel, Field
from typing import Optional, List


class UploadedBy(BaseModel):
    uploaded_by_id: Optional[str] = Field(None, example="1234")
    uploaded_by_type: Optional[str] = Field(None, example="user")


class HorseCreate(BaseModel):
    name: str = Field(..., example="Bobby")
    year_of_birth: int = Field(..., example=2015)
    breed: str = Field(..., example="Thoroughbred")
    size: int = Field(..., example=150000)
    gender: str = Field(..., example="Gelding")
    description: str = Field(..., example="A horse for the future.")
    price_sar: int = Field(..., example=50000)
    # images: List[str] = Field(..., example=["http://example.com/image1.jpg", "http://example.com/image2.jpg"])
    # uploaded_by: UploadedBy = Field(...)

class HorseRentResponse(BaseModel):
    horse_renting_service_id: str

class HorseSaleResponse(BaseModel):
    horse_selling_service_id: str