from typing import Optional, List
from data.db import get_clubs_collection
from logging_config import log
from models.clubs import ClubInternal

club_collection = get_clubs_collection()


def get_all_clubs_logic() -> Optional[List[Optional[ClubInternal]]]:
    pass


def get_club_by_id_logic(club_id: str) -> ClubInternal | None:
    pass


def get_club_with_services_and_trainer(club_id: str):
    pass


def get_club_by_user_id_logic(user_id: str) -> ClubInternal | None:
    pass


def find_club(**kwargs) -> Optional[ClubInternal]:
    log.info(f"inside find_club({kwargs})")

    club = club_collection.find_one(kwargs)

    if not club:
        log.info(f"No club exists with the provided attributes, returning None")
        return None

    retval = ClubInternal(**club)

    log.info(f"returning club = {retval}")

    return retval

