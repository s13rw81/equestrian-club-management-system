from typing import Optional

from pydantic import BaseModel, field_validator

from utils.image_management import generate_image_url

from . import GetTrainerDTO


class GetTrainerCertificationDTO(BaseModel):
    id: str
    name: str
    number: str
    image: Optional[str] = None
    trainer_id: str

    @field_validator("image")
    def convert_image_id_to_url(cls, image):
        if not image:
            return image
        return generate_image_url(image_id=image)


class GetTrainerSpecializationDTO(BaseModel):
    id: str
    name: str
    years_of_experience: int
    trainer_id: str


class GetTrainerDetailedDTO(GetTrainerDTO):
    certifications: list[GetTrainerCertificationDTO] = []
    # specializations: list[GetTrainerSpecializationDTO] = []
