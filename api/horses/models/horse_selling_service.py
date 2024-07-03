from pydantic import BaseModel, Field
from models.logistics_company_services.logistics_company_services import Provider
from typing import Optional, List, Union


class HorseSellingItem(BaseModel):
    id: str = Field(..., example="abcd1234")  # Updated to 'id'
    horse_id: str = Field(..., example="horse5678")
    provider: Provider
    price_sar: float = Field(..., example=50000)

class SellerInformation(BaseModel):
    name: Optional[str] = Field(None, example="user.name / club.name")
    email_address: Optional[str] = Field(None, example="fXXXXXXXXX@gmail.com")
    phone_no: Optional[str] = Field(None, example="+91XXXXXXXXXX")
    location: Optional[str] = Field(None, example="user.address / club.address")

class HorseSellingResponse(BaseModel):
    horse_selling_service_id: Optional[str] = Field(None, example="horse_selling_service._id")
    horse_id: Optional[str] = Field(None, example="horses._id")
    name: Optional[str] = Field(None, example="horses.name")
    year_of_birth: Optional[int] = Field(None, example=2010)
    breed: Optional[str] = Field(None, example="horses.breed")
    size: Optional[int] = Field(None, example="horses.size")
    gender: Optional[str] = Field(None, example="horses.gender")
    description: Optional[str] = Field(None, example="horses.description")
    image_urls: Optional[List[str]] = Field(None, example=["horses.images[0]", "horses.images[1]"])
    price: Optional[float] = Field(None, example=50000)
    seller_information: Optional[SellerInformation] = None



