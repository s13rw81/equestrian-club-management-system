from pydantic import BaseModel, Field

class HorseSellingItem(BaseModel):
    provider_id: str = Field(..., example="1234")
    provider_type: str = Field(..., example="user")
    price: float = Field(..., example=50000)
