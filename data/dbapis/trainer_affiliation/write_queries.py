from data.db import get_trainer_affiliation_collection
from logging_config import log
from models.trainer_affiliation import TrainerAffiliationInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction

trainer_affiliation_collection = get_trainer_affiliation_collection()


@atomic_transaction
def save_trainer_affiliation(
        new_trainer_affiliation: TrainerAffiliationInternal,
        session=None
) -> TrainerAffiliationInternal:

    log.info(f"inside save_trainer_affiliation(new_trainer_affiliation={new_trainer_affiliation})")

    result = trainer_affiliation_collection.insert_one(new_trainer_affiliation.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new trainer_affiliation can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new trainer_affiliation can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new trainer_affiliation has successfully been inserted "
             f"(trainer_affiliation_id={new_trainer_affiliation.id})")

    return new_trainer_affiliation