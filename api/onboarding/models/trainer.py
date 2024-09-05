from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from models.trainer.trainer import SocialMediaLinks
from utils.date_time import get_current_utc_datetime
from utils.trainer import (
    get_default_preferred_time_slots,
    get_default_trainer_availability,
)


class BaseTrainer(BaseModel):
    full_name: str
    email_address: EmailStr
    phone_no: Optional[str] = None
    years_of_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    training_location: Optional[str] = None
    available_services: Optional[List[str]] = None
    availability: Optional[str] = Field(
        default_factory=get_default_trainer_availability,
        min_length=7,
        max_length=7,
        pattern="^[TF]{7}$",
    )
    prefferred_time_slots: Optional[str] = Field(
        default_factory=get_default_preferred_time_slots,
        min_length=3,
        max_length=3,
        pattern="^[TF]{3}$",
    )
    social_media_links: Optional[SocialMediaLinks] = None
    biography: Optional[str] = Field(default=None, max_length=100)
    expertise: Optional[List[str]] = None
    levels_taught: Optional[List[str]] = None
    club_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, fields):
        for k, v in fields.items():
            if isinstance(v, str) and v == "":
                raise ValueError(f"{k} should not be an empty string")

            if isinstance(v, list):
                for field in v:
                    if isinstance(field, str) and field == "":
                        raise ValueError(f"values of {k} should not be empty string")
        return fields

    @field_validator("social_media_links")
    @classmethod
    def validate_social_media_links(cls, links):
        none_count = 0
        for link in links:
            if link[1] is None:
                none_count += 1
                continue

            if link[0] == "website":
                continue

            if link[0] not in link[1].host:
                raise ValueError(f"{link[1]} should be a valid {link[0]} url")

        if none_count == 5:
            raise ValueError("atleast one of the social media links should be present")

        return links


class AddTrainer(BaseTrainer): ...


class ResponseAddTrainer(BaseModel):
    trainer_id: str


class UpdateTrainer(BaseTrainer):
    full_name: Optional[str] = None
    email_address: Optional[EmailStr] = None

    @computed_field
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()


class ViewTrainer(BaseModel):
    full_name: Optional[str] = None
    email_address: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    years_of_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    training_location: Optional[str] = None
    available_services: Optional[List[str]] = None
    availability: Optional[str] = None
    prefferred_time_slots: Optional[str] = None
    social_media_links: Optional[SocialMediaLinks] = None
    biography: Optional[str] = None
    expertise: Optional[List[str]] = None
    levels_taught: Optional[List[str]] = None
    club_id: Optional[str] = None
    certification_urls: List[str] = Field(default=None, alias="certifications")
    profile_file_urls: List[str] = Field(default=None, alias="profile_files")
    profile_picture_url: Optional[str] = Field(default=None, alias="profile_picture")


class ResponseGetTrainer(BaseModel):
    full_name: Optional[str] = None
    email_address: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    years_of_experience: Optional[int] = None
    specializations: Optional[List[str]] = None
    training_location: Optional[str] = None
    available_services: Optional[List[str]] = None
    availability: Optional[str] = None
    prefferred_time_slots: Optional[str] = None
    social_media_links: Optional[SocialMediaLinks] = None
    biography: Optional[str] = None
    expertise: Optional[List[str]] = None
    levels_taught: Optional[List[str]] = None
    club_id: Optional[str] = None
    certification_urls: List[str] = None
    profile_file_urls: List[str] = None
    profile_picture_url: Optional[str] = None
