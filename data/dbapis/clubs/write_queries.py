from fastapi import HTTPException, status

from data.db import (
    get_club_service_availability_collection,
    get_clubs_collection,
    get_clubs_service_collection,
)
from decorators import atomic_transaction
from logging_config import log
from models.clubs import ClubInternal, UpdateClubInternal
from models.clubs.service_internal import (
    AvailabilityInternal,
    ClubServiceInternal,
    UpdateClubServiceInternal,
)

from . import find_club

club_collection = get_clubs_collection()
club_service_collection = get_clubs_service_collection()
club_service_availability_collection = get_club_service_availability_collection()


@atomic_transaction
def save_club(new_club: ClubInternal, session=None) -> ClubInternal:

    log.info(f"inside save_club(new_club={new_club})")

    result = club_collection.insert_one(new_club.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new club can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new club can't be inserted in the database due to unknown reasons...",
        )

    log.info(f"new club has successfully been inserted (club_id={new_club.id})")

    return new_club


@atomic_transaction
def update_club(update_club_data: UpdateClubInternal, session=None) -> ClubInternal:
    log.info(f"inside update_club(update_club_data={update_club_data})")
    club_database_id = str(update_club_data.id)

    update_club_dict = update_club_data.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": club_database_id}

    result = club_collection.update_one(
        update_filter, {"$set": update_club_dict}, session=session
    )

    log.info(
        f"club update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update club due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="club cannot be updated in the database due to unknown reasons",
        )

    updated_club = find_club(id=club_database_id, session=session)

    return updated_club


@atomic_transaction
def save_club_service(
    club_service: ClubServiceInternal, session=None
) -> ClubServiceInternal:

    log.info(f"inside save_club_service(new_club_service={club_service})")

    result = club_service_collection.insert_one(
        club_service.model_dump(), session=session
    )

    if not result.acknowledged:
        log.info(
            "new club_service can't be inserted in the database, raising exception..."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new club service can't be inserted in the database due to unknown reasons...",
        )

    log.info(
        f"new club service has successfully been inserted (club_service_id={club_service.id})"
    )

    return club_service


@atomic_transaction
def update_club_service(
    update_club_service_data: UpdateClubServiceInternal, session=None
) -> ClubServiceInternal:
    log.info(
        f"inside update_club_service(update_club_service_data={update_club_service_data})"
    )
    club_service_db_id = str(update_club_service_data.id)

    update_filter = {"id": club_service_db_id}
    update_club_service_dict = update_club_service_data.model_dump(
        exclude={"id"}, exclude_unset=True
    )

    result = club_service_collection.update_one(
        update_filter,
        {"$set": update_club_service_dict},
        session=session,
    )

    log.info(
        f"club service update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info(
            "could not update club service due to unknown reasons, raising exception"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="club service cannot be updated in the database due to unknown reasons",
        )

    # for now returning None
    return


@atomic_transaction
def save_club_service_availability(
    service_availability: list[AvailabilityInternal], session=None
) -> list[AvailabilityInternal]:

    log.info(
        f"inside save_club_service_availability(availability={service_availability})"
    )

    result = club_service_availability_collection.insert_many(
        [availability.model_dump() for availability in service_availability]
    )

    if not result.acknowledged:
        log.info(
            "club service availability can't be inserted in the database, raising exception..."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="club service availability can't be inserted in the database due to unknown reasons...",
        )

    availability_ids = [availability.id for availability in service_availability]

    log.info(
        f"club service availability has successfully been inserted (service_availability_ids={availability_ids})"
    )

    return service_availability


@atomic_transaction
def update_club_service_availability(
    update_availability: list[AvailabilityInternal], club_service_id: str, session=None
) -> AvailabilityInternal:
    log.info(
        f"inside update_club_service_availability(update_availability={update_availability})"
    )

    update_filter = {"id": club_service_id}

    for availability in update_availability:
        update_filter = {
            "id": club_service_id,
        }

    club_service_availability_collection.update_many()

    result = club_service_collection.update_one(
        update_filter,
        {"$set": update_club_service_data.model_dump()},
        session=session,
    )

    log.info(
        f"club service update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info(
            "could not update club service due to unknown reasons, raising exception"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="club service cannot be updated in the database due to unknown reasons",
        )

    # for now returning None
    return
