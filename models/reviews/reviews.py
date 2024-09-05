from typing import Optional

from data.db import PyObjectId
from models.user import UserRoles
from pydantic import BaseModel, Field, field_serializer
from bson import ObjectId


class Reviewee(BaseModel):
    reviewee_id: str
    reviewee_type: UserRoles

    @field_serializer("reviewee_type")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value


class Reviewer(BaseModel):
    reviewer_id: str
    reviewer_type: UserRoles

    @field_serializer('reviewer_type')
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value


class Review(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    reviewee: Reviewee
    reviewer: Reviewer
    rating: float
    review: Optional[str]
    approved_by_khayyal_admin: bool = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
