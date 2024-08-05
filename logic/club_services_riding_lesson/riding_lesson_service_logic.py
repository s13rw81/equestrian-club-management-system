from data.db import get_riding_lesson_collection, get_clubs_collection, get_users_collection, get_riding_lesson_bookings_collection
from data.dbapis.club_services_riding_lessons.read_queries import get_existing_riding_lesson_service_for_club
from data.dbapis.club_services_riding_lessons.write_queries import insert_riding_instance_to_club, add_trainers_to_riding_service, create_new_riding_lesson_service_booking
from fastapi import HTTPException
from logging_config import log
from models.logistics_company_services import Provider
from models.services_riding_lession.riding_lession_booking_model import RidingLessonBooking
from models.services_riding_lession.riding_lesson_service_model import RidingLessonService, RidingLessonServicePricingOption
from models.user import UserRoles
from starlette import status

riding_lesson_collection = get_riding_lesson_collection()
clubs_collection = get_clubs_collection()
users_collection = get_users_collection()
riding_lesson_bookings_collection = get_riding_lesson_bookings_collection()


def attach_riding_lesson_to_club_logic(club_id: str, price: dict):
    log.info(f"attach riding lesson to club with id {club_id} with price: {price}")

    res = get_existing_riding_lesson_service_for_club(club_id)
    if res:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER,
                            detail='horse riding serice already attached for club')
    # make a provider instance
    provider_instance = Provider(provider_id=club_id, provider_type=UserRoles.CLUB.value)
    # make a new riding lesson instance
    price_instance = RidingLessonServicePricingOption(**price['pricing_options'][0])
    new_riding_lesson_service_instance = RidingLessonService(provider=provider_instance,
                                                             pricing_options=[price_instance])
    res = insert_riding_instance_to_club(new_riding_lesson_service_instance)
    if res:
        msg = f'riding lesson service attached to club : {club_id}, riding lession service id : {res.inserted_id}'
        log.info(msg)
        return msg


def get_riding_lesson_by_club_id_logic(club_id):
    res = get_existing_riding_lesson_service_for_club(club_id)
    if not res:
        raise HTTPException(status_code=404, detail=f'no riding lesson service found for club {club_id}')
    return res


def attach_trainers_to_riding_service_of_club_logic(club_id, trainers: list[str] = list()):
    log.info(f'attach_trainers_to_riding_service_of_club_logic {club_id}, {trainers}')
    res = add_trainers_to_riding_service(club_id, trainers)
    return res


def create_riding_lesson_service_booking(booking: dict, club_id: str, user_id: str):
    log.info(f'creating a booking for user {user_id} with club {club_id} for riding lesson with details {booking}')

    riding_lesson_service_id_for_club = get_existing_riding_lesson_service_for_club(club_id=club_id)

    booking = RidingLessonBooking(
        user_id=user_id,
        riding_lesson_service_id=riding_lesson_service_id_for_club['id'],
        trainer_id=booking['trainer_id'],
        selected_date=booking['selected_date'],
        pricing_option=booking['pricing_option'],
        number_of_visitors=booking['number_of_visitors']
    )
    result = create_new_riding_lesson_service_booking(booking.model_dump())
    if result.inserted_id:
        return result.inserted_id
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='error creating booking')
