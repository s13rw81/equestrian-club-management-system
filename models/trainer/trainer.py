from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime


class SocialMediaLinks(BaseModel):
    website: Optional[AnyUrl] = None
    linkedin: Optional[AnyUrl] = None
    instagram: Optional[AnyUrl] = None
    facebook: Optional[AnyUrl] = None
    twitter: Optional[AnyUrl] = None


class TrainerInternal(BaseModel):
    full_name: str
    email_address: EmailStr
    phone_no: Optional[str]
    years_of_experience: Optional[int]
    specializations: Optional[List[str]]
    training_location: Optional[str]
    available_services: Optional[List[str]]
    availability: Optional[str]
    prefferred_time_slots: Optional[str]
    social_media_links: Optional[SocialMediaLinks]
    biography: Optional[str]
    expertise: Optional[List[str]]
    levels_taught: Optional[List[str]]
    club_id: Optional[str]
    user_id: Optional[str]
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    certifications: Optional[List[str]] = None
    profile_files: Optional[List[str]] = None
    profile_picture: Optional[str] = None


class TrainerInternalWithID(TrainerInternal):
    trainer_id: Annotated[PyObjectId, str] = Field(default=None, alias="_id")
