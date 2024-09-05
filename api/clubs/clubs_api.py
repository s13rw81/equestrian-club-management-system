from typing import Annotated, Optional, List

from api.clubs.models.book_generic_activity_request_model import GenericActivityBookingRequest
from api.clubs.models.book_horse_shoeing_request_model import HorseShoeingBookingRequest
from api.clubs.models.book_riding_lesson_request_model import RidingLessonBookingRequest
from api.clubs.models.ratings_request_model import ClubReview
from api.onboarding import UpdateClubRequest
from data.dbapis.club_services_generic_activity.read_queries import get_all_existing_generic_activity_service, \
    get_existing_generic_activity_service_bookings_by_user_id, get_existing_generic_activity_service_for_club, \
    get_all_existing_generic_activity_service_bookings_for_club, get_all_existing_generic_activity_service_bookings
from data.dbapis.club_services_horse_shoeing.read_queries import get_existing_horse_shoeing_service_for_club, \
    get_all_existing_horse_shoeing_service_bookings, get_existing_horse_shoeing_service_bookings_for_club, \
    get_existing_horse_shoeing_service_bookings_by_user_id
from data.dbapis.club_services_riding_lessons.read_queries import get_existing_riding_lesson_service_for_club, \
    get_existing_riding_lesson_service_booking_by_user_id, \
    get_riding_lesson_service_bookings_by_riding_lesson_id, get_existing_riding_lesson_service_bookings
from data.dbapis.clubs.delete_queries import delete_club_by_id_logic
from data.dbapis.clubs.read_queries import get_all_clubs_logic, get_club_by_id_logic, \
    get_club_with_services_and_trainer, get_club_by_user_id_logic
from data.dbapis.trainer.read_queries import get_trainer_by_club_id
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from logging_config import log
from logic.auth import get_current_user
from logic.club_services_generic_activity.generic_activity_service import create_generic_activity_service_booking_logic
from logic.club_services_horse_shoeing.horse_shoeing_service_logic import create_horse_shoeing_service_booking_logic
from logic.club_services_riding_lesson.riding_lesson_service_logic import create_riding_lesson_service_booking
from logic.clubs.club_reviews import check_existing_review_by_user_for_club, add_review_for_club_by_user
from models.clubs import ClubExternal
from models.clubs import ClubInternal
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from role_based_access_control import RoleBasedAccessControl

clubs_api_router = APIRouter(
    prefix="/user/club",
    tags=["user-club"]
)


@clubs_api_router.get("/get-clubs")
async def get_all_clubs(user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> Optional[
    List[ClubExternal]]:
    # TODO: [phase ii] pagination
    # TODO: [phase ii] add filtering
    user_ext = UserExternal(**user.model_dump())
    log.info(f"getting list of clubs, user: {user}")
    result = get_all_clubs_logic()
    log.info(f"result {result}, user: {user_ext}")
    return result


@clubs_api_router.get("/get-club-details/{club_id}")
async def get_club_details_by_club_id(user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))],
                                      club_id: str) -> ClubExternal | None:
    """
    :param user:
    :param club_id: id of the club to be fetched
    :return: instance of ClubInternal, details of the club
    """
    user_ext = UserExternal(**user.model_dump())
    log.info(f"fetching club with id: {club_id}, user is {user_ext}")

    club = get_club_with_services_and_trainer(club_id)

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    club['id'] = str(club['_id'])
    club['riding_lesson_service'] = club['riding_lesson_service'][0]
    club['horse_shoeing_service'] = club['horse_shoeing_service'][0]
    club['generic_activity_service'] = club['generic_activity_service'][0]
    log.info(f"club fetched with id: {club_id} by user {user_ext}")
    return club


@clubs_api_router.put("/{club_id}")
async def update_club_by_id(club_id: str, user: Annotated[UserExternal, Depends(get_current_user)],
                            update_club: UpdateClubRequest) -> dict[str, str | int]:
    """
    :param club_id: id of the club to be updated
    :param user: user invoking the api
    :param update_club: instance of UpdateClub dto
    :return: instance of str, id of updated club
    """

    # TODO: check if user has permission to update club
    # TODO: add apis to delete club images
    user_ext = UserExternal(**user.model_dump())
    log.info(f"updating club with id: {club_id}, user: {user_ext}")

    existing_club = get_club_by_id_logic(club_id)
    if not existing_club:
        raise HTTPException(status_code=404, detail="Club not found")

    # TODO: add check to allow only admins to update club details
    # if existing_club.created_by.email_address != user.email_address:
    #     raise HTTPException(status_code = 403, detail = "User does not have permission to update this club")

    updated_club_details = ClubInternal(
        name=update_club.name if update_club.name else existing_club.name,
        description=update_club.description if update_club.description else existing_club.description,
        price=update_club.price if update_club.price else existing_club.price,
        image_urls=update_club.image_urls if update_club.image_urls else existing_club.image_urls,
        address=update_club.address if update_club.address else existing_club.address,
        contact=update_club.contact if update_club.contact else existing_club.contact,
        admins=update_club.admins if update_club.admins else existing_club.admins
    )
    result = update_club(club_id=club_id, updated_club=updated_club_details)

    if not result:
        raise HTTPException(status_code=404, detail="Club not found or not updated")

    msg = f"club with id: {club_id} updated by user: {user_ext}"
    log.info(msg)
    return {'status_code': 200, 'details': msg, 'data': result}


@clubs_api_router.delete("/{club_id}")
async def delete_club(club_id: str, user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    """
    :param club_id:
    :param user: user invoking the api
    :return: status message
    """
    user_ext = UserExternal(**user.model_dump())
    log.info(f"deleting club, user: {user}")
    # Check if the user is the creator of the club
    club = get_club_by_id_logic(club_id)
    if not club:
        emsg = f'club with id {club_id} not found.'
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )
    for admin in club.admins:
        if user.id == admin.id:
            # Delete the club
            result = delete_club_by_id_logic(club_id=club_id)
            msg = f"club deleted with id: {club_id} by user: {user_ext}"
            return {'status_code': 200, 'details': msg, 'data': result}

    return {'status_code': 403, 'detail': 'User does not have permission to delete this club'}


@clubs_api_router.post("/rate-a-club")
async def rate_and_review_club(club_review: ClubReview, user: Annotated[
    UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    log.info(f"adding user: {user}'s review for club {club_review.club_id}")

    existing_review = check_existing_review_by_user_for_club(club_review=club_review, user=user)
    if existing_review:
        emsg = f'review for club with id {club_review.club_id} by user already exists.'
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail=emsg)
    else:
        res = add_review_for_club_by_user(club_review, user)
        if res:
            log.info(f'review for club added.')
            return {"review_id": str(res.inserted_id)}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='error adding review for club')


@clubs_api_router.post("/book-riding-lesson-service/{club_id}")
async def book_riding_lesson_service(club_id: str, booking: RidingLessonBookingRequest, user: Annotated[
    UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    log.info(f"booking user: {user}'s riding_lesson_service with club {club_id}")

    # match trainer and club
    trainer_instance = get_trainer_by_club_id(club_id=club_id)
    if trainer_instance.trainer_id != booking.trainer_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='trainer not associated with club.')

    # match pricing options
    riding_lesson_service = get_club_with_services_and_trainer(club_id=club_id).get('riding_lesson_service', None)
    if not riding_lesson_service:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='no riding lesson service for club')

    # check if pricing option of booking is offered
    booking_pricing_option_is_valid = booking.pricing_option in riding_lesson_service[0]['pricing_options']
    if not booking_pricing_option_is_valid:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='pricing option not offered by club')

    booking_dict = booking.model_dump(exclude_none=True)
    result = create_riding_lesson_service_booking(booking=booking_dict, club_id=club_id, user_id=user.id)

    return {"riding_lesson_service_booking_id": str(result)}


@clubs_api_router.post("/book-generic-activity-service/{club_id}")
async def book_generic_activity_service(club_id: str, booking: GenericActivityBookingRequest, user: Annotated[
    UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    log.info(f"booking user: {user}'s generic_activity_service with club {club_id}")

    # match trainer and club
    trainer_instance = get_trainer_by_club_id(club_id=club_id)
    if trainer_instance.trainer_id != booking.trainer_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='trainer not associated with club.')

    # match pricing options
    generic_activity_service = get_club_with_services_and_trainer(club_id=club_id).get('generic_activity_service', None)
    if not generic_activity_service:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='no riding lesson service for club')

    # # check if pricing option of booking is offered
    # booking_pricing_option_is_valid = booking.pricing_option in generic_activity_service[0]['pricing_options']
    # if not booking_pricing_option_is_valid:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='pricing option not offered by club')

    booking_dict = booking.model_dump(exclude_none=True)
    result = create_generic_activity_service_booking_logic(booking=booking_dict, club_id=club_id, user_id=user.id)

    return {"generic_activity_service_booking_id": str(result)}


@clubs_api_router.post("/book-horse-shoeing-service/{club_id}")
async def book_horse_shoeing_service(club_id: str, booking: HorseShoeingBookingRequest, user: Annotated[
    UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    log.info(f"booking user: {user}'s horse_shoeing_service with club {club_id}")

    # match trainer and club
    trainer_instance = get_trainer_by_club_id(club_id=club_id)
    if trainer_instance.trainer_id != booking.trainer_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='trainer not associated with club.')

    # match pricing options
    horse_shoeing_service = get_club_with_services_and_trainer(club_id=club_id).get('horse_shoeing_service', None)
    if not horse_shoeing_service:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='no riding lesson service for club')

    # check if pricing option of booking is offered
    booking_pricing_option_is_valid = booking.pricing_option in horse_shoeing_service[0]['pricing_options']
    if not booking_pricing_option_is_valid:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='pricing option not offered by club')

    booking_dict = booking.model_dump(exclude_none=True)
    result = create_horse_shoeing_service_booking_logic(booking=booking_dict, club_id=club_id, user_id=user.id)

    return {"horse_shoeing_service_booking_id": str(result)}


@clubs_api_router.get("/get-generic-activity-service-booking")
async def get_generic_activty_bookings(user: Annotated[UserExternal, Depends(get_current_user)]):
    log.info(f'get_generic_activty_bookings called by user {user}')

    # get user's booking
    if user.user_role == UserRoles.USER:
        res = get_existing_generic_activity_service_bookings_by_user_id(user.id)

    # get user's booking
    if user.user_role == UserRoles.CLUB:
        club = get_club_by_user_id_logic(user_id=user.id)
        generic_activity_service_id = get_existing_generic_activity_service_for_club(club['id'])
        res = get_all_existing_generic_activity_service_bookings_for_club(generic_activity_service_id['id'])

    # get user's booking
    if user.user_role == UserRoles.ADMIN:
        res = get_all_existing_generic_activity_service_bookings()

    return res


@clubs_api_router.get("/get-horse-shoeing-service-booking")
async def get_horse_shoeing_service_booking(user: Annotated[UserExternal, Depends(get_current_user)]):
    log.info(f'get_horse_shoeing_service_booking called by user {user}')

    # get user's booking
    if user.user_role == UserRoles.USER:
        res = get_existing_horse_shoeing_service_bookings_by_user_id(user.id)

    # get user's booking
    if user.user_role == UserRoles.CLUB:
        club = get_club_by_user_id_logic(user_id=user.id)
        horse_shoeing_service = get_existing_horse_shoeing_service_for_club(club['id'])
        res = get_existing_horse_shoeing_service_bookings_for_club(horse_shoeing_service['id'])

    # get user's booking
    if user.user_role == UserRoles.ADMIN:
        res = get_all_existing_horse_shoeing_service_bookings()

    return res


@clubs_api_router.get("/get-riding-lesson-service-booking")
async def get_riding_lesson_service_booking(user: Annotated[UserExternal, Depends(get_current_user)]):
    res = []
    log.info(f'get_riding_lesson_service_booking called by user {user}')

    # get user's booking
    if user.user_role == UserRoles.USER:
        res = get_existing_riding_lesson_service_booking_by_user_id(user.id)

    # get user's booking
    if user.user_role == UserRoles.CLUB:
        club = get_club_by_user_id_logic(user.id)
        res = get_existing_riding_lesson_service_for_club(club['id'])
        riding_lesson_service_id = res['id']
        res = get_riding_lesson_service_bookings_by_riding_lesson_id(riding_lesson_service_id)

    # get user's booking
    if user.user_role == UserRoles.ADMIN:
        res = get_existing_riding_lesson_service_bookings()

    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no ridiing lesson service bookings associated with user')

    return res

