from pydantic import BaseModel, Field


class Provider(BaseModel):
    provider_id: str = Field(..., example="1234")
    provider_type: str = Field(..., example="user")


class HorseRentingItem(BaseModel):
    id: str = Field(..., example="abcd1234")  # Updated to 'id'
    horse_id: str = Field(..., example="horse5678")
    provider: Provider
    price_sar: float = Field(..., example=50000)
