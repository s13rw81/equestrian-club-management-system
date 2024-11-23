from ..common_base import CommonBase
from typing import Optional


class TrainerCertificationInternal(CommonBase):
    # user-fields
    name: str
    number: str

    # system-fields
    # the id of the associated image
    image: Optional[str] = None
    # the id of the corresponding trainer
    trainer_id: str