from data.db import get_trainer_specializations_collection
from logging_config import log
from models.trainer_specialization import TrainerSpecializationInternal, UpdateTrainerSpecializationInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from pymongo import UpdateOne
from . import find_trainer_specializations_with_ids

trainer_specializations_collection = get_trainer_specializations_collection()


@atomic_transaction
def save_trainer_specializations_bulk(
        new_trainer_specializations: list[TrainerSpecializationInternal],
        session=None
) -> list[TrainerSpecializationInternal]:
    log.info(f"inside save_trainer_specializations_bulk(new_trainer_specializations={new_trainer_specializations})")

    if not new_trainer_specializations:
        log.info(f"returning {new_trainer_specializations}")
        return new_trainer_specializations

    new_trainer_specializations_dumped = [
        new_trainer_specialization.model_dump() for new_trainer_specialization in new_trainer_specializations
    ]

    result = trainer_specializations_collection.insert_many(new_trainer_specializations_dumped, session=session)

    if not result.acknowledged:
        log.info("new trainer specializations can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new trainer specializations can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new trainer specializations have successfully been inserted")

    return new_trainer_specializations


@atomic_transaction
def update_trainer_specializations_bulk(
        update_trainer_specialization_dtos: list[UpdateTrainerSpecializationInternal],
        session=None
) -> list[TrainerSpecializationInternal]:
    log.info(f"inside update_trainer_specializations_bulk("
             f"update_trainer_specialization_dtos={update_trainer_specialization_dtos})")

    updates = []

    for update_trainer_specialization_dto in update_trainer_specialization_dtos:
        trainer_specialization_database_id = str(update_trainer_specialization_dto.id)

        update_trainer_specialization_dict = update_trainer_specialization_dto.model_dump(exclude={"id"},
                                                                                        exclude_unset=True)

        update_filter = {"id": trainer_specialization_database_id}

        updates.append(
            UpdateOne(update_filter, {"$set": update_trainer_specialization_dict})
        )

    result = trainer_specializations_collection.bulk_write(
        updates,
        session=session
    )

    log.info(
        f"trainer specializations update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update trainer specializations due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="trainer specializations cannot be updated in the database due to unknown reasons"
        )

    updated_trainer_specializations = find_trainer_specializations_with_ids(
        trainer_specialization_ids=[
            str(update_trainer_specialization_dto.id)
            for update_trainer_specialization_dto in update_trainer_specialization_dtos
        ],
        session=session
    )

    log.info(f"returning {updated_trainer_specializations}")

    return updated_trainer_specializations
