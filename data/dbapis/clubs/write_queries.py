from data.db import get_clubs_collection
from fastapi import HTTPException
from logging_config import log
from models.clubs.clubs_internal import ClubInternal
from fastapi import status


club_collection = get_clubs_collection()


def save_club(new_club: ClubInternal) -> str:
    """
        saves the new user in the database and returns the id
        :param new_club: ClubInternal
        :returns: id
    """
    log.info(f"save_club invoked: {new_club}")

    # Check if a club with the same name and city already exists
    existing_club = club_collection.find_one({"name": new_club.name, "address.city": new_club.address.city})

    if existing_club is not None:
        emsg = f"Club with name {new_club.name} and city {new_club.address.city} already exists."
        log.info(emsg)
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER,
            detail = emsg
        )

    club_id = (club_collection.insert_one(new_club.model_dump())).inserted_id
    retval = str(club_id)
    log.info(f"new club created with id: {retval}")
    return retval

