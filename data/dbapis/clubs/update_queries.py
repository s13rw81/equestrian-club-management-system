from bson import ObjectId
from data.db import get_clubs_collection
from models.clubs.clubs_internal import ClubInternal

clubs_collection = get_clubs_collection()


def update_club_by_id_logic(updated_club: ClubInternal, club_id: str = None) -> str:
    """
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """

    # Convert the updated_club from pydantic model to dictionary
    updated_club_dict = updated_club.model_dump()

    # Update the club in the database
    result = clubs_collection.update_one({'_id': ObjectId(club_id)}, {'$set': updated_club_dict})

    return result.modified_count == 1
