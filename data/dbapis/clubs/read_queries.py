from typing import Optional, List

from bson.errors import InvalidId
from bson.objectid import ObjectId
from data.db import async_get_clubs_collection
from logging_config import log
from models.clubs.clubs_external import ClubExternal


async def async_get_clubs() -> Optional[List[Optional[ClubExternal]]]:
    """
        get all the clubs instances
        :returns: all of clubs as list of dicts
    """
    club_collection = await async_get_clubs_collection()
    log.info(f"get_all_clubs invoked")
    # clubs = [club for club in (await club_collection.find())]
    # retval = UserInternal(**user, id = str(user['_id']))
    all_clubs = club_collection.find({})
    clubs = list()
    for club in all_clubs:
        clubs.append(ClubExternal(**club, id=str(club['_id'])))
    log.info(f"returning {clubs}")
    return clubs


async def async_get_club_by_id(club_id: str) -> ClubExternal | None:
    """
    :param club_id: id of the club to be fetched
    :return: instance of ClubInternal, details of the club
    """

    # get the clubs collection
    clubs = await async_get_clubs_collection()

    club = None

    # fetch the club
    try:
        club = clubs.find_one({"_id": ObjectId(club_id)})
    except InvalidId as e:
        log.error(f'{e} :  club_id')
    finally:
        if club:
            return ClubExternal(**club, id=str(club['_id']))

    return None
