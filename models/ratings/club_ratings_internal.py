from pydantic import BaseModel


class ClubRatingsInternal(BaseModel):
    club: str
    user: str
    rating: int
