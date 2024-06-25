from typing import Optional, List

from bson.errors import InvalidId
from bson.objectid import ObjectId
from data.db import get_clubs_collection
from logging_config import log
from models.clubs import ClubInternal
from models.clubs.clubs_external import ClubExternal

club_collection = get_clubs_collection()


def get_all_clubs_logic() -> Optional[List[Optional[ClubExternal]]]:
    """
        get all the clubs instances
        :returns: all of clubs as list of dicts
    """

    log.info(f"get_all_clubs invoked")
    # clubs = [club for club in (await club_collection.find())]
    # retval = UserInternal(**user, id = str(user['_id']))
    all_clubs = club_collection.find({})
    clubs = list()
    for club in all_clubs:
        clubs.append(ClubInternal(**club))
    log.info(f"returning {clubs}")
    return clubs


def get_club_by_id_logic(club_id: str) -> ClubExternal | None:
    """
    :param club_id: id of the club to be fetched
    :return: instance of ClubInternal, details of the club
    """

    club = None

    # fetch the club
    try:
        club = club_collection.find_one({"_id": ObjectId(club_id)})
    except InvalidId as e:
        log.error(f'{e} :  club_id')
    finally:
        if club:
            return ClubInternal(**club)

    return None
