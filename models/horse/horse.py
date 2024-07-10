from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from models.user.enums.user_roles import UserRoles
from utils.date_time import get_current_utc_datetime


class UploadInfo(BaseModel):
    uploaded_by_id: str
    uploaded_by_user: UserRoles

    @field_serializer("uploaded_by_user")
    def enum_serializer(self, enum):
        return enum.value


class HorseInternal(BaseModel):
    name: str
    year_of_birth: str
    breed: str
    size: str
    gender: str
    description: str
    images: Optional[List[str]] = []
    uploaded_by: UploadInfo
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
