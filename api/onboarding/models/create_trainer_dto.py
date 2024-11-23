from pydantic import BaseModel, constr, field_validator, Field
from data.dbapis.trainer_affiliation import find_trainer_affiliation
from logging_config import log
from models.trainers.enums import AvailableService, WeekDay, TimeSlot

class CreateTrainerCertificationDTO(BaseModel):
    name: constr(min_length=1, max_length=200)
    number: constr(min_length=1, max_length=200)

class CreateTrainerSpecializationDTO(BaseModel):
    name: constr(min_length=1, max_length=200)
    years_of_experience: int = Field(gt=0)

class CreateTrainerDTO(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    bio: constr(min_length=1, max_length=1000)
    club_affiliation_number: str
    available_services: list[AvailableService]
    availability: list[WeekDay]
    preferred_time_slot: TimeSlot
    # using `default_factory` instead of `default` to preserve the nested key names in the openapi schema
    certifications: list[CreateTrainerCertificationDTO] = Field(default_factory=list)
    specializations: list[CreateTrainerSpecializationDTO] = Field(default_factory=list)

    @field_validator("full_name")
    def full_name_capitalize(cls, full_name):
        return " ".join([item.capitalize() for item in full_name.split()])

    @field_validator("club_affiliation_number")
    def validate_club_affiliation_number(cls, club_affiliation_number):
        result = find_trainer_affiliation(id=club_affiliation_number)

        if not result:
            log.info(f"invalid club_affiliation_number: {club_affiliation_number}, "
                     "raising ValueError...")

            raise ValueError(f"invalid club_affiliation_number: {club_affiliation_number}, "
                             "raising ValueError...")
        return club_affiliation_number
