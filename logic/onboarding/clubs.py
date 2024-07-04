from api import UpdateClubRequest
from bson import ObjectId
from data.db import get_clubs_collection
from data.dbapis.clubs import get_club_by_id_logic
from fastapi import HTTPException
from logging_config import log
from models.clubs import ClubInternal
from models.user import UserInternal
from starlette import status

clubs_collection = get_clubs_collection()


def update_club_by_id_logic(user: UserInternal, updated_club: UpdateClubRequest, club_id: str = None) -> str:
    """
    :param user: userInternal
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """
    log.info(f"updating club data")
    existing_club = get_club_by_id_logic(club_id = club_id)

    if existing_club and user.id not in existing_club['users']:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'user is does not have privilege to use this route.'
        )

    # Convert the updated_club from pydantic model to dictionary
    updated_club_dict = updated_club.model_dump(exclude_none = True)

    updated_club_request = ClubInternal(
        name = updated_club_dict['name'] if 'name' in updated_club_dict and updated_club_dict['name'] else
        existing_club['name'],
        phone_no = updated_club_dict['phone_no'] if 'phone_no' in updated_club_dict and updated_club_dict[
            'phone_no'] else existing_club['phone_no'],
        description = updated_club_dict['description'] if 'description' in updated_club_dict and
                                                          updated_club_dict['description'] else existing_club[
            'description'],
        is_khayyal_verified = updated_club_dict[
            'is_khayyal_verified'] if 'is_khayyal_verified' in updated_club_dict and updated_club_dict[
            'is_khayyal_verified'] else existing_club['is_khayyal_verified'],
        images = updated_club_dict['images'] if 'images' in updated_club_dict and updated_club_dict['images'] else
        existing_club['images'],
        email_address = updated_club_dict['email_address'] if 'email_address' in updated_club_dict and
                                                              updated_club_dict['email_address'] else existing_club[
            'email_address'],
        address = updated_club_dict['address'] if 'address' in updated_club_dict and
                                                  updated_club_dict['address'] else existing_club[
            'address'])

    # Update the club in the database
    result = clubs_collection.update_one({'_id': ObjectId(club_id)}, {'$set': updated_club_request.model_dump()})

    return result.modified_count == 1
