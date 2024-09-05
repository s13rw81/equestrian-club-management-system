from typing import Optional

from pydantic import BaseModel, Field


class ClubReview(BaseModel):
    club_id: str = Field(..., description="The ID of the club")
    rating: int = Field(..., ge=1, le=5, description="Rating of the club (1 to 5)")
    review: str = Optional[Field(..., description="Review of the club")]
