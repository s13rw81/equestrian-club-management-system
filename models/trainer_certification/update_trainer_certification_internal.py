from ..common_base import CommonBase
from typing import Optional

class UpdateTrainerCertificationInternal(CommonBase):
    # user-fields
    name: str = None
    number: str = None

    # system-fields
    image_id: Optional[str] = None