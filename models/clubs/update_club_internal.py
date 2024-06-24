from typing import Optional, List


class UpdateClubInternal:
    name: str
    description: Optional[str]
    price: float
    image_urls: Optional[List[str]]
