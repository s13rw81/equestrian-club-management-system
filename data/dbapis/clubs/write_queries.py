from data.db import get_clubs_collection
from logging_config import log
from models.clubs import ClubInternal, UpdateClubInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from . import find_club

club_collection = get_clubs_collection()


@atomic_transaction
def save_club(new_club: ClubInternal, session=None) -> ClubInternal:
    """
        saves the new user in the database and returns the id
        :param new_club: ClubInternal
        :param session: database transaction session
        :returns: ClubInternal
    """
    log.info(f"inside save_club(new_club={new_club})")

    result = club_collection.insert_one(new_club.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new club can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new club can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new club has successfully been inserted (club_id={new_club.id})")

    return new_club

@atomic_transaction
def update_club(update_club_data: UpdateClubInternal, session=None) -> ClubInternal:
    log.info(f"inside update_club(update_club_data={update_club_data})")
    club_database_id = update_club_data.id.hex

    update_club_dict = update_club_data.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": club_database_id}

    result = club_collection.update_one(
        update_filter,
        {"$set": update_club_dict},
        session=session
    )

    log.info(
        f"club update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update club due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="club cannot be updated in the database due to unknown reasons"
        )

    updated_club = find_club(id=club_database_id, session=session)

    return updated_club
