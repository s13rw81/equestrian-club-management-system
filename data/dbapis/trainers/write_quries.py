from data.db import get_trainer_collection
from logging_config import log
from models.trainers import TrainerInternal, UpdateTrainerInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from . import find_trainer

trainer_collection = get_trainer_collection()


@atomic_transaction
def save_trainer(new_trainer: TrainerInternal, session=None) -> TrainerInternal:

    log.info(f"inside save_trainer(new_trainer={new_trainer})")

    result = trainer_collection.insert_one(new_trainer.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new trainers can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new trainers can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new trainers has successfully been inserted (trainer_id={new_trainer.id})")

    return new_trainer

@atomic_transaction
def update_trainer(update_trainer_dto: UpdateTrainerInternal, session=None) -> TrainerInternal:
    log.info(f"inside update_trainer(update_trainer_dto={update_trainer_dto})")
    trainer_database_id = str(update_trainer_dto.id)

    update_trainer_dict = update_trainer_dto.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": trainer_database_id}

    result = trainer_collection.update_one(
        update_filter,
        {"$set": update_trainer_dict},
        session=session
    )

    log.info(
        f"trainers update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update trainers due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="trainers cannot be updated in the database due to unknown reasons"
        )

    updated_trainer = find_trainer(id=trainer_database_id, session=session)

    return updated_trainer