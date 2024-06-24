from pydantic import BaseModel


class DeleteClubRequest(BaseModel):
    club_id: str
