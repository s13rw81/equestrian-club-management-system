from typing import List, Optional

from api.onboarding.models import RidingLessonServicePricingOption
from pydantic import BaseModel, Field

from bson import ObjectId
from data.db import PyObjectId
from models.logistics_company_services import Provider


class RidingLessonService(BaseModel):
    id: Optional[PyObjectId] = Field(alias = '_id', default = None)
    provider: Provider
    pricing_options: List[RidingLessonServicePricingOption]

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {PyObjectId: str}

