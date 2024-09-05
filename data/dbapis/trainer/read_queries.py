from typing import Union

from bson import ObjectId
from data.db import get_trainer_collection
from logging_config import log
from models.trainer.trainer import TrainerInternalWithID, TrainerSlim

trainer_collection = get_trainer_collection()


def get_trainer_details_by_email_db(
        email_address: str,
) -> Union[TrainerInternalWithID, None]:
    """return trainer details based on email address

    Args:
        email_address (str): email address of the trainer

    Returns:
        Union[TrainerInternalWithID, None]
    """

    log.info(f"get_trainer_details_by_email_db() called {email_address}")

    filter = {"email_address": email_address}

    response = trainer_collection.find_one(filter=filter)
    retval = TrainerInternalWithID(**response) if response else response

    log.info(f"get_trainer_details_by_email_db returning {retval}")

    return retval


def get_trainer_by_club_id(club_id: str) -> Union[TrainerSlim, None]:
    """return trainer details based on club id

    Args:
        club_id (str): id of the club

    Returns:
        Union[TrainerInternalWithID, None]
    """

    log.info(f"get_trainer_by_club_id() called {club_id}")

    response = trainer_collection.find_one(filter={"club_id": club_id})
    retval = TrainerSlim(**response) if response else response

    log.info(f"get_trainer_by_club_id returning {retval}")

    return retval


def get_trainer_by_trainer_id(trainer_id: str) -> Union[TrainerSlim, None]:
    """return trainer details based on club id

    Args:
        trainer_id (str): id of the trainer

    Returns:
        Union[TrainerInternalWithID, None]
    """

    log.info(f"get_trainer_by_trainer_id() called {trainer_id}")

    response = trainer_collection.find_one(filter={"_id": ObjectId(trainer_id)})
    retval = TrainerSlim(**response) if response else response

    log.info(f"get_trainer_by_trainer_id returning {retval}")

    return retval
