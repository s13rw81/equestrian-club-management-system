from pydantic import BaseModel, constr, Field, field_validator
from data.dbapis.clubs import find_club
from logging_config import log

class CreateTrainerDTO(BaseModel):
    full_name: constr(min_length=1, max_length=200)
    club_affiliation: str = Field(..., description="associated club_id")

    @field_validator("club_affiliation")
    def validate_club_affiliation(cls, club_affiliation):
        log.info(f"inside validate_club_affiliation(club_affiliation={club_affiliation})")

        club = find_club(id=club_affiliation)

        if not club:
            log.info(f"invalid club_id = {club_affiliation}, raising ValueError...")
            raise ValueError(f"invalid club_id={club_affiliation}")

        return club_affiliation

