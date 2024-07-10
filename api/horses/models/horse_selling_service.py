from datetime import datetime
from typing import Annotated, List, Optional, Union

from pydantic import (
    AfterValidator,
    BaseModel,
    computed_field,
    field_validator,
    model_validator,
)

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime
from utils.mask_information import mask_email, mask_phone_number


class EnlistHorseForSell(BaseModel):
    name: str
    year_of_birth: str
    breed: str
    size: str
    gender: str
    description: str
    price: str


class EnlistHorseForSellResponse(BaseModel):
    horse_selling_service_id: str


class SellerInformation(BaseModel):
    name: str
    email_address: Annotated[Union[str, None], AfterValidator(mask_email)]
    phone_no: Annotated[Union[str, None], AfterValidator(mask_phone_number)]
    location: Optional[str] = None


class GetHorseSellListing(BaseModel):
    horse_selling_service_id: Annotated[PyObjectId, str]
    horse_id: str
    name: str
    year_of_birth: str
    breed: str
    size: str
    gender: str
    description: str
    image_urls: List[str]
    price: str
    seller_information: SellerInformation


class UpdateHorseForSellServiceListing(BaseModel):
    name: Optional[str] = None
    year_of_birth: Optional[str] = None
    breed: Optional[str] = None
    size: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()


class HorseSellEnquiry(BaseModel):
    horse_selling_service_id: str
    message: str


class CreateSellEnquiryResponse(BaseModel):
    horse_selling_enquiry_id: str


class UpdateHorseSellEnquiry(BaseModel):
    message: Optional[str] = None


class GetHorseSellEnquiry(BaseModel):
    horse_selling_enquiry_id: str
    horse_selling_service_id: str
    user_id: str
    message: str
    created_at: datetime
    updated_at: datetime
