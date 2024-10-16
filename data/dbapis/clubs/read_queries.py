from typing import Optional, List
from data.db import get_clubs_collection
from decorators import atomic_transaction
from logging_config import log
from models.clubs import ClubInternal

club_collection = get_clubs_collection()


def get_club_count() -> int:
    log.info("inside get_club_count()")
    club_count = club_collection.count_documents({})

    log.info(f"returning {club_count}")
    return club_count


@atomic_transaction
def find_club(session=None, **kwargs) -> Optional[ClubInternal]:
    log.info(f"inside find_club({kwargs})")

    club = club_collection.find_one(kwargs, session=session)

    if not club:
        log.info(f"No club exists with the provided attributes, returning None")
        return None

    retval = ClubInternal(**club)

    log.info(f"returning club = {retval}")

    return retval


@atomic_transaction
def find_club_by_user(user_id, session=None) -> Optional[ClubInternal]:
    log.info(f"inside find_club_by_user(user_id={user_id})")

    club = club_collection.find_one({"users.user_id": user_id}, session=session)

    if not club:
        log.info("no club is associated with the provided user_id, returning None")
        return None

    retval = ClubInternal(**club)

    log.info(f"returning club = {retval}")

    return retval

@atomic_transaction
def find_many_clubs(session=None, **kwargs) -> list[ClubInternal]:
    log.info(f"inside find_many_clubs({kwargs})")

    clubs_cursor = club_collection.find(kwargs, session=session)

    retval = [ClubInternal(**club) for club in clubs_cursor]

    log.info(f"returning {retval}")

    return retval