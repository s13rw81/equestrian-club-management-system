from typing import Optional
from data.db import get_trainer_certifications_collection
from decorators import atomic_transaction
from logging_config import log
from models.trainer_certification import TrainerCertificationInternal

trainer_certification_collection = get_trainer_certifications_collection()


@atomic_transaction
def find_trainer_certification(session=None, **kwargs) -> Optional[TrainerCertificationInternal]:
    log.info(f"inside find_trainer_certification({kwargs})")

    trainer_certification = trainer_certification_collection.find_one(kwargs, session=session)

    if not trainer_certification:
        log.info(f"No trainer certification exists with the provided attributes, returning None")
        return None

    retval = TrainerCertificationInternal(**trainer_certification)

    log.info(f"returning trainer_certification = {retval}")

    return retval


@atomic_transaction
def find_trainer_certifications_with_ids(
        trainer_certification_ids: list[str],
        session=None
) -> list[TrainerCertificationInternal]:
    log.info(f"inside find_trainer_certifications_with_ids(trainer_certifications_ids={trainer_certification_ids})")

    trainer_certification_cursor = trainer_certification_collection.find(
        {"id": {"$in": trainer_certification_ids}},
        session=session
    )

    retval = [TrainerCertificationInternal(**trainer_certification)
              for trainer_certification in trainer_certification_cursor]

    log.info(f"returning {retval}")

    return retval
