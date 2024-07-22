from typing import Union

from data.db import get_trainer_collection
from logging_config import log
from models.trainer.trainer import TrainerInternalWithID

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
