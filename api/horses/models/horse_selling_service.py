from pydantic import BaseModel, Field
from models.logistics_company_services.logistics_company_services import Provider


class HorseSellingItem(BaseModel):
    id: str = Field(..., example="abcd1234")  # Updated to 'id'
    horse_id: str = Field(..., example="horse5678")
    provider: Provider
    price_sar: float = Field(..., example=50000)
