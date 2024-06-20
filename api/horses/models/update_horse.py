from pydantic import BaseModel, Field
from typing import Optional


class HorseUpdate(BaseModel):
    name: Optional[str] = Field(
        None, example="Thunderbolt")
    description: Optional[str] = Field(
        None, example="A fast and reliable horse.")
    year: Optional[int] = Field(
        None, example=2015)
    height_cm: Optional[int] = Field(
        None, example=160)
    club_name: Optional[str] = Field(
        None, example="Sunset Riders Club")
    price_sar: Optional[int] = Field(
        None, example=50000)
    image_url: Optional[str] = Field(
        None, example="http://example.com/image.jpg")
    contact_seller_url: Optional[str] = Field(
        None, example="http://example.com/contact")
    go_transport_url: Optional[str] = Field(
        None, example="http://example.com/transport")
