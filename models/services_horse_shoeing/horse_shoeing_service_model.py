from typing import List, Optional

from api.onboarding.models import HorseShoeingServicePricingOption
from pydantic import BaseModel, Field

from bson import ObjectId
from data.db import PyObjectId
from models.logistics_company_services import Provider


class HorseShoeingService(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    provider: Provider
    pricing_options: List[HorseShoeingServicePricingOption]

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {PyObjectId: str}
