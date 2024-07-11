from typing import Optional, List

from pydantic import BaseModel


class UpdateClubRequest(BaseModel):
    email_address: Optional[str] = None
    phone_no: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_khayyal_verified: bool = None
    image_urls: Optional[List[str]] = []
    users: Optional[List] = []
