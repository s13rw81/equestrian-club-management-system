from typing import List, Optional

from data.db import (
    get_club_service_availability_collection,
    get_clubs_collection,
    get_clubs_service_collection,
)
from decorators import atomic_transaction
from logging_config import log
from models.clubs import ClubInternal
from models.clubs.service_internal import AvailabilityInternal, ClubServiceInternal

club_collection = get_clubs_collection()
club_service_collection = get_clubs_service_collection()
availability_collection = get_club_service_availability_collection()


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


@atomic_transaction
def find_club_service(
    club_service_id: str, session=None
) -> Optional[ClubServiceInternal]:
    log.info(f"inside find_club_service(club_service_id={club_service_id})")

    club_service = club_service_collection.find_one(
        {"id": club_service_id}, session=session
    )

    if not club_service:
        log.info(
            "no club service is associated with the provided club service id, returning None"
        )
        return None

    retval = ClubServiceInternal(**club_service)

    log.info(f"returning club_service = {retval}")

    return retval


@atomic_transaction
def get_club_service_availability(
    club_service_id: str, availability_id: str, session=None
) -> AvailabilityInternal:
    log.info(
        f"inside find_club_service_availability(club_service_id={club_service_id}, availability_id={availability_id})"
    )

    club_service_availability = availability_collection.find_one(
        filter={"id": availability_id, "club_service_id": club_service_id},
        session=session,
    )

    if not club_service_availability:
        log.info(
            f"no club service found for service_id {club_service_id} and availability_id {availability_id}"
        )
        return None

    retval = AvailabilityInternal(**club_service_availability)

    log.info(f"returning club_service_availability = {retval}")

    return retval
