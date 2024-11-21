from typing import Optional
from data.db import get_trainer_collection
from decorators import atomic_transaction
from logging_config import log
from models.trainers import TrainerInternal

trainer_collection = get_trainer_collection()

@atomic_transaction
def find_trainer(session=None, **kwargs) -> Optional[TrainerInternal]:
    log.info(f"inside find_trainer({kwargs})")

    trainer = trainer_collection.find_one(kwargs, session=session)

    if not trainer:
        log.info(f"No trainer exists with the provided attributes, returning None")
        return None

    retval = TrainerInternal(**trainer)

    log.info(f"returning trainer = {retval}")

    return retval

@atomic_transaction
def find_many_trainers(session=None, **kwargs) -> list[TrainerInternal]:
    log.info(f"inside find_many_trainers({kwargs})")

    trainers_cursor = trainer_collection.find(kwargs, session=session)

    retval = [TrainerInternal(**trainer) for trainer in trainers_cursor]

    log.info(f"returning {retval}")

    return retval