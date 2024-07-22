from data.db import get_trainer_collection
from logging_config import log
from models.trainer.trainer import TrainerInternal

trainer_collection = get_trainer_collection()


def add_trainer(trainer: TrainerInternal) -> str:
    """add a new trainer to the database and return the id

    Args:
        trainer (TrainerInternal): trainer_details

    Returns:
        str: id of the new trainer
    """

    log.info(f"add_trainer() called trainer_details {trainer}")

    response = trainer_collection.insert_one(trainer.model_dump())
    retval = str(response.inserted_id)

    log.info(f"add_trainer() returning {retval}")

    return retval


def update_trainer_details(update_details: dict, user_id: str) -> bool:
    """update the details of a trainer based on user_id

    Args:
        update_details (dict)
    """

    log.info(f"update_trainer_details() called update_details {update_details}")

    filter = {"user_id": user_id}
    response = trainer_collection.update_one(
        filter=filter, update={"$set": update_details}
    )

    return response.modified_count == 1
