from pydantic import BaseModel, Field, field_validator, constr
from data.dbapis.clubs import find_club
from data.dbapis.trainers import find_trainer
from logging_config import log
from uuid import UUID

class UpdateTrainerDTO(BaseModel):
    id: UUID = Field(..., description="trainer_id")
    full_name: constr(min_length=1, max_length=200) = None
    club_affiliation: str = Field(None, description="associated club_id")

    @field_validator("id")
    def validate_id(self, trainer_id):
        log.info(f"inside validate_id(trainer_id={trainer_id})")

        trainer = find_trainer(id=str(trainer_id))

        if not trainer:
            log.info(f"invalid trainer_id={trainer_id}, raising ValueError...")
            raise ValueError(f"invalid trainer_id={trainer_id}")

        return trainer_id

    @field_validator("club_affiliation")
    def validate_club_affiliation(cls, club_affiliation):
        log.info(f"inside validate_club_affiliation(club_affiliation={club_affiliation})")

        club = find_club(id=club_affiliation)

        if not club:
            log.info(f"invalid club_id={club_affiliation}, raising ValueError...")
            raise ValueError(f"invalid club_id={club_affiliation}")

        return club_affiliation