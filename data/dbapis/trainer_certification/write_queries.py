from data.db import get_trainer_certification_collection
from logging_config import log
from models.trainer_certification import TrainerCertificationInternal, UpdateTrainerCertificationInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from pymongo import UpdateOne
from . import find_trainer_certifications_with_ids

trainer_certification_collection = get_trainer_certification_collection()


@atomic_transaction
def save_trainer_certifications_bulk(
        new_trainer_certifications: list[TrainerCertificationInternal],
        session=None
) -> list[TrainerCertificationInternal]:
    log.info(f"inside save_many_trainer_certifications(new_trainer_certifications={new_trainer_certifications})")

    new_trainer_certifications_dumped = [
        new_trainer_certification.model_dump() for new_trainer_certification in new_trainer_certifications
    ]

    result = trainer_certification_collection.insert_many(new_trainer_certifications_dumped, session=session)

    if not result.acknowledged:
        log.info("new trainer certifications can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new trainer certifications can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new trainer certifications have successfully been inserted")

    return new_trainer_certifications


@atomic_transaction
def update_trainer_certifications_bulk(
        update_trainer_certification_dtos: list[UpdateTrainerCertificationInternal],
        session=None
) -> list[TrainerCertificationInternal]:
    log.info(f"inside update_trainer_certifications_bulk("
             f"update_trainer_certification_dtos={update_trainer_certification_dtos})")

    updates = []

    for update_trainer_certification_dto in update_trainer_certification_dtos:
        trainer_certification_database_id = str(update_trainer_certification_dto.id)

        update_trainer_certification_dict = update_trainer_certification_dto.model_dump(exclude={"id"},
                                                                                        exclude_unset=True)

        update_filter = {"id": trainer_certification_database_id}

        updates.append(
            UpdateOne(update_filter, {"$set": update_trainer_certification_dict})
        )

    result = trainer_certification_collection.bulk_write(
        updates,
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

    updated_trainer_certifications = find_trainer_certifications_with_ids(
        trainer_certification_ids=[
            str(update_trainer_certification_dto.id)
            for update_trainer_certification_dto in update_trainer_certification_dtos
        ],
        session=session
    )

    log.info(f"returning {updated_trainer_certifications}")

    return updated_trainer_certifications
