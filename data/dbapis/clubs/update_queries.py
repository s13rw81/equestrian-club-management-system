from bson import ObjectId
from data.db import async_get_clubs_collection
from models.clubs.clubs_internal import ClubInternal


async def async_update_club_by_id(updated_club: ClubInternal, existing_club: ClubInternal = None,
                                  club_id: str = None) -> str:
    """
    :param existing_club:
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """
    if not existing_club:
        pass

    clubs_collection = await async_get_clubs_collection()
    # Convert the updated_club from pydantic model to dictionary
    updated_club_dict = updated_club.model_dump()

    # Update the club in the database
    result = clubs_collection.update_one({'_id': ObjectId(club_id)}, {'$set': updated_club_dict})

    return result.modified_count == 1
