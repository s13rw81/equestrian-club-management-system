from typing import Any

from api.onboarding.models.update_club_model import UpdateClubRequest
from bson import ObjectId
from data.db import get_clubs_collection
from data.dbapis.clubs import get_club_by_id_logic
from data.dbapis.onboarding.onboarding_clubs.read_queries import get_clubs
from fastapi import HTTPException
from logging_config import log
from models.clubs import ClubInternal
from models.user import UserInternal
from fastapi import status

clubs_collection = get_clubs_collection()


def update_club_by_id_logic(updated_club: UpdateClubRequest, club_id: str = None) -> str:
    """
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """
    log.info(f"updating club data")
    existing_club = get_club_by_id_logic(club_id=club_id)

    # Convert the updated_club from pydantic model to dictionary
    updated_club_dict = updated_club.model_dump(exclude_none=True)

    updated_club_request = ClubInternal(
        name=updated_club_dict['name'] if 'name' in updated_club_dict and updated_club_dict['name'] else existing_club['name'],
        phone_no=updated_club_dict['phone_no'] if 'phone_no' in updated_club_dict and updated_club_dict['phone_no'] else existing_club['phone_no'],
        description=updated_club_dict['description'] if 'description' in updated_club_dict and updated_club_dict['description'] else existing_club['description'],
        is_khayyal_verified=updated_club_dict['is_khayyal_verified'] if 'is_khayyal_verified' in updated_club_dict and updated_club_dict['is_khayyal_verified'] else existing_club['is_khayyal_verified'],
        image_urls=existing_club['image_urls'] + updated_club_dict['image_urls'] if 'image_urls' in updated_club_dict and updated_club_dict['image_urls'] else existing_club['image_urls'],
        email_address=updated_club_dict['email_address'] if 'email_address' in updated_club_dict and updated_club_dict['email_address'] else existing_club['email_address'],
        address=updated_club_dict['address'] if 'address' in updated_club_dict and updated_club_dict['address'] else existing_club['address'],
        users=existing_club['users'] + updated_club_dict['users'] if 'users' in updated_club_dict and updated_club_dict['users'] else existing_club['users'],
    )

    # Update the club in the database
    result = clubs_collection.update_one({'_id': ObjectId(club_id)}, {'$set': updated_club_request.model_dump()})

    return result.modified_count == 1


def get_club_id_of_user(user: UserInternal) -> str | None:
    log.info(f'checking which club user belongs to {user.full_name}')

    # Query the Club collection
    clubs = get_clubs()

    for club in clubs:
        for club_user in club['users']:
            if club_user['user_id'] == user.id:
                return club

    return None
