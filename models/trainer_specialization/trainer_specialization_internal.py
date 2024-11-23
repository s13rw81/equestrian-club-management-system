from ..common_base import CommonBase


class TrainerSpecializationInternal(CommonBase):
    # user-fields
    name: str
    years_of_experience: int

    # system-fields
    # the id of the corresponding trainer
    trainer_id: str
