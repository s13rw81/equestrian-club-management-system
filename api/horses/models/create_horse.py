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
    image_urls: Optional[List[str]] = None

class HorseRentResponse(BaseModel):
    horse_renting_service_id: str

class HorseSaleResponse(BaseModel):
    horse_id: str
    horse_selling_service_id: str



class SellerInformation(BaseModel):
    name: str
    email_address: str
    phone_no: str
    location: str

class HorseSellingItem(BaseModel):
    horse_selling_service_id: str
    horse_id: str
    name: str
    year_of_birth: int
    breed: str
    size: str
    gender: str
    description: str
    image_urls: List[str]
    price: float
    seller_information: SellerInformation