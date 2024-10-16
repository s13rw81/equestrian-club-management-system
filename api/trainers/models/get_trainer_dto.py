from pydantic import BaseModel
from uuid import UUID


class GetTrainerDTO(BaseModel):
    id: UUID
    club_affiliation: str
    full_name: str
    user_id: str