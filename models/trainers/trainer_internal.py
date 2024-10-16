from ..common_base import CommonBase

class TrainerInternal(CommonBase):
    # the id of the club the trainer is affiliated with
    club_affiliation: str
    full_name: str
    # the id of the user that manages this Trainer entity
    user_id: str
