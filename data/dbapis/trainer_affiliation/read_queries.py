from decorators import atomic_transaction
from typing import Optional
from models.trainer_affiliation import TrainerAffiliationInternal
from logging_config import log
from data.db import get_trainer_affiliation_collection

trainer_affiliation_collection = get_trainer_affiliation_collection()


@atomic_transaction
def find_trainer_affiliation(session=None, **kwargs) -> Optional[TrainerAffiliationInternal]:
    log.info(f"inside find_trainer_affiliation({kwargs})")

    trainer_affiliation = trainer_affiliation_collection.find_one(kwargs, session=session)

    if not trainer_affiliation:
        log.info(f"No trainer_affiliation exists with the provided attributes, returning None")
        return None

    retval = TrainerAffiliationInternal(**trainer_affiliation)

    log.info(f"returning trainer_affiliation = {retval}")

    return retval

@atomic_transaction
def find_many_trainer_affiliations(session=None, **kwargs) -> list[TrainerAffiliationInternal]:
    log.info(f"inside find_many_trainer_affiliations({kwargs})")

    trainer_affiliation_cursor = trainer_affiliation_collection.find(kwargs, session=session)

    retval = [TrainerAffiliationInternal(**trainer_affiliation) for trainer_affiliation in trainer_affiliation_cursor]

    log.info(f"returning {retval}")

    return retval