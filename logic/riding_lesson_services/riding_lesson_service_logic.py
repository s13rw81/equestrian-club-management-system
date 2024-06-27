from api.riding_lesson_services.models.book_riding_lesson_request_model import BookRidinglessonRequest
from bson import ObjectId
from data.db import get_riding_lesson_collection, get_clubs_collection, get_users_collection, \
    get_riding_lesson_bookings_collection
from data.dbapis.riding_lessons.riding_lesson_logic import insert_riding_instance_to_club, get_riding_lesson_by_club_id, \
    add_trainers_to_riding_service, check_existing_riding_service_for_club
from fastapi import HTTPException
from logging_config import log
from models.riding_lession_services.riding_lession_booking_model import RidingLessonBooking
from models.logistics_company_services import Provider
from models.riding_lession_services.riding_lesson_service_model import RidingLessonService
from models.user import UserRoles
from models.user.user_external import UserExternal
from starlette import status

riding_lesson_collection = get_riding_lesson_collection()
clubs_collection = get_clubs_collection()
users_collection = get_users_collection()
riding_lesson_bookings_collection = get_riding_lesson_bookings_collection()


def attach_riding_lesson_to_club_logic(club_id: str, price: float = 0.0, description = None):
    log.info(f"attach riding lesson to club with id {club_id} with price: {price}")

    res = check_existing_riding_service_for_club(club_id)
    if res:
        raise HTTPException(
            status_code = status.HTTP_303_SEE_OTHER, detail = 'horse riding serice already attached for club'
        )
    # make a provider instance
    provider_instance = Provider(provider_id = club_id, provider_type = UserRoles.CLUB.value)
    # make a new riding lesson instance

    new_riding_lesson_serivice_instance = RidingLessonService(
        description = description,
        provider = provider_instance,
        price = price
    )
    res = insert_riding_instance_to_club(new_riding_lesson_serivice_instance)
    if res:
        msg = f'riding lesson service attached to club {club_id}, res : {res}'
        log.info(msg)
        return msg


def get_riding_lesson_by_club_id_logic(club_id):
    res = get_riding_lesson_by_club_id(club_id)
    if not res:
        raise HTTPException(status_code = 404, detail = f'no riding lesson service found for club {club_id}')
    return res


def attach_trainers_to_riding_service_of_club_logic(club_id, trainers: list[str] = list()):
    log.info(f'attach_trainers_to_riding_service_of_club_logic {club_id}, {trainers}')
    res = add_trainers_to_riding_service(club_id, trainers)
    return res


def book_horse_riding_lesson(riding_lesson_instance: BookRidinglessonRequest):
    log.info(f'creating a booking for horse riding lesson, {riding_lesson_instance}')
    # Fetch the corresponding data from the collections
    lesson = riding_lesson_collection.find_one({"_id": ObjectId(riding_lesson_instance.lesson_service)})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson service not found")

    club_id = lesson['provider']['provider_id']
    club = clubs_collection.find_one({"_id": ObjectId(club_id)})
    if not club:
        raise HTTPException(status_code=404, detail="provider club not found")

    rider = users_collection.find_one({"_id": ObjectId(riding_lesson_instance.rider)})
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    trainer = users_collection.find_one({"_id": ObjectId(riding_lesson_instance.trainer)})
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Create the RidingLessonBooking instance
    booking = RidingLessonBooking(
        lesson_service=RidingLessonService(**lesson),
        rider=UserExternal(**rider),
        trainer=UserExternal(**trainer),
        lesson_datetime=riding_lesson_instance.lesson_datetime,
        venue=request.venue if riding_lesson_instance.venue else club['address'],
        payment_status=riding_lesson_instance.payment_status,
        booking_status=riding_lesson_instance.booking_status
    )

    # Insert the booking into the RidingLessonBooking collection
    try:
        result = riding_lesson_bookings_collection.insert_one(booking.model_dump())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

