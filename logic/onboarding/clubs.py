from api.onboarding.models.update_club_model import UpdateClubRequest
from data.dbapis.club_services_riding_lessons.read_queries import get_existing_riding_lesson_service_for_club
from data.dbapis.club_services_riding_lessons.write_queries import update_riding_lesson_service
from data.dbapis.clubs import get_club_by_id_logic, save_club
from data.dbapis.user import update_user
from data.dbapis.onboarding.onboarding_clubs.read_queries import get_clubs
from data.dbapis.onboarding.onboarding_clubs.write_queries import update_club
from logging_config import log
from models.clubs import ClubInternal
from models.services_riding_lession.riding_lesson_service_model import RidingLessonService
from models.user import UserInternal, UpdateUserInternal, UserRoles
from decorators import atomic_transaction


@atomic_transaction
def create_club(club: ClubInternal, user: UserInternal, session=None) -> ClubInternal:

    log.info(f"inside create_club(club={club}, user={user})")

    newly_created_club = save_club(new_club=club, session=session)

    update_user_data = UpdateUserInternal(
        user_role=UserRoles.CLUB
    )

    update_user(update_user_data=update_user_data, user=user, session=session)

    log.info(f"returning {newly_created_club}")

    return newly_created_club

def update_club_by_id_logic(updated_club: UpdateClubRequest, club_id: str = None) -> str:
    """
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """
    log.info(f"updating club data")
    existing_club = get_club_by_id_logic(club_id = club_id)

    # Convert the updated_club from pydantic model to dictionary
    updated_club_dict = updated_club.model_dump(exclude_none = True)

    updated_club_request = ClubInternal(
        name = updated_club_dict['name'] if 'name' in updated_club_dict and updated_club_dict['name'] else existing_club['name'],
        location = updated_club_dict['location'] if 'location' in updated_club_dict and updated_club_dict['location'] else existing_club['location'],
        phone_no = updated_club_dict['phone_no'] if 'phone_no' in updated_club_dict and updated_club_dict['phone_no'] else existing_club['phone_no'],
        description = updated_club_dict['description'] if 'description' in updated_club_dict and updated_club_dict['description'] else existing_club['description'],
        is_khayyal_verified = updated_club_dict['is_khayyal_verified'] if 'is_khayyal_verified' in updated_club_dict and updated_club_dict['is_khayyal_verified'] else existing_club['is_khayyal_verified'],
        image_urls = existing_club['image_urls'] + updated_club_dict['image_urls'] if 'image_urls' in updated_club_dict and updated_club_dict['image_urls'] else existing_club['image_urls'],
        email_address = updated_club_dict['email_address'] if 'email_address' in updated_club_dict and updated_club_dict['email_address'] else existing_club['email_address'],
        address = updated_club_dict['address'] if 'address' in updated_club_dict and updated_club_dict['address'] else existing_club['address'],
        users = existing_club['users'] + updated_club_dict['users'] if 'users' in updated_club_dict and updated_club_dict['users'] else existing_club['users'],
    )

    # Update the club in the database
    result = update_club(club_id = club_id, updated_club_request = updated_club_request.model_dump())
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


def update_riding_lesson_service_by_club_id_logic(club_id: str, updated_club: UpdateClubRequest) -> str:
    """
    :param club_id: id of the club to be updated
    :param updated_club: instance of ClubInternal with updated details
    :return: instance of str, id of updated club
    """
    log.info(f"updating riding lesson service by club id logic")
    # Convert the updated_club from pydantic model to dictionary
    updated_riding_lesson_service_instance = updated_club.model_dump(exclude_none = True).get('riding_lesson_service', None)
    if not updated_riding_lesson_service_instance:
        return True

    existing_riding_lesson_service = get_existing_riding_lesson_service_for_club(club_id = club_id)

    updated_riding_lesson_service_request = RidingLessonService(
        pricing_options = updated_riding_lesson_service_instance['pricing_options'] if 'pricing_options' in updated_riding_lesson_service_instance and updated_riding_lesson_service_instance['pricing_options'] else existing_riding_lesson_service['pricing_options'],
        provider = updated_riding_lesson_service_instance['provider'] if 'provider' in updated_riding_lesson_service_instance and updated_riding_lesson_service_instance['provider'] else existing_riding_lesson_service['provider'],
    )

    # Update the club in the database
    result = update_riding_lesson_service(riding_lesson_service_id = existing_riding_lesson_service['id'], updated_riding_lesson_service_request = updated_riding_lesson_service_request.model_dump())
    return result.modified_count == 1
