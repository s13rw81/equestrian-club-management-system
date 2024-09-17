from data.db import get_clubs_collection
from logging_config import log
from models.clubs.clubs_internal import ClubInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction

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


