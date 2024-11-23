from typing import Optional
from data.db import get_trainer_specializations_collection
from decorators import atomic_transaction
from logging_config import log
from models.trainer_specialization import TrainerSpecializationInternal

trainer_specializations_collection = get_trainer_specializations_collection()


@atomic_transaction
def find_trainer_specialization(session=None, **kwargs) -> Optional[TrainerSpecializationInternal]:
    log.info(f"inside find_trainer_specialization({kwargs})")

    trainer_specializations = trainer_specializations_collection.find_one(kwargs, session=session)

    if not trainer_specializations:
        log.info(f"No trainer specialization exists with the provided attributes, returning None")
        return None

    retval = TrainerSpecializationInternal(**trainer_specializations)

    log.info(f"returning trainer_specialization = {retval}")

    return retval


@atomic_transaction
def find_trainer_specializations_with_ids(
        trainer_specialization_ids: list[str],
        session=None
) -> list[TrainerSpecializationInternal]:
    log.info(f"inside find_trainer_specializations_with_ids(trainer_specialization_ids={trainer_specialization_ids})")

    trainer_specialization_cursor = trainer_specializations_collection.find(
        {"id": {"$in": trainer_specialization_ids}},
        session=session
    )

    retval = [TrainerSpecializationInternal(**trainer_specialization)
              for trainer_specialization in trainer_specialization_cursor]

    log.info(f"returning {retval}")

    return retval
