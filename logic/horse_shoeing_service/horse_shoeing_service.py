from api.onboarding.models import UpdateClubRequest
from api.onboarding.models import HorseShoeingServicePricingOption
from api.riding_lesson_services.models.book_riding_lesson_request_model import BookRidinglessonRequest
from bson import ObjectId
from data.db import get_riding_lesson_collection, get_clubs_collection, get_users_collection, get_riding_lesson_bookings_collection
from data.dbapis.club_services_horse_shoeing.read_queries import get_existing_horse_shoeing_service_for_club, \
    get_existing_horse_shoeing_service_for_club
from data.dbapis.club_services_horse_shoeing.write_queries import insert_horse_shoeing_instance_to_club, update_horse_shoeing_service
from data.dbapis.club_services_riding_lessons.write_queries import add_trainers_to_riding_service
from fastapi import HTTPException
from logging_config import log
from models.services_horse_shoeing.horse_shoeing_service_model import HorseShoeingService
from models.logistics_company_services import Provider
from models.services_riding_lession.riding_lession_booking_model import RidingLessonBooking
from models.services_riding_lession.riding_lesson_service_model import RidingLessonService
from models.user import UserRoles
from models.user.user_external import UserExternal
from starlette import status

riding_lesson_collection = get_riding_lesson_collection()
clubs_collection = get_clubs_collection()
users_collection = get_users_collection()
riding_lesson_bookings_collection = get_riding_lesson_bookings_collection()


def attach_horse_shoeing_service_to_club_logic(club_id: str, price: dict):
    log.info(f"attaching horse shoeing service to club with id {club_id} with price: {price}")

    res = get_existing_horse_shoeing_service_for_club(club_id)
    if res:
        raise HTTPException(status_code = status.HTTP_303_SEE_OTHER, detail = 'horse shoeing serice already attached to club')

    # make a provider instance
    provider_instance = Provider(provider_id = club_id, provider_type = UserRoles.CLUB.value)

    # make a new horse shoeing service instance
    price_instance = HorseShoeingServicePricingOption(**price['pricing_options'][0])
    new_horse_shoeing_service_instance = HorseShoeingService(provider = provider_instance, pricing_options = [price_instance])
    res = insert_horse_shoeing_instance_to_club(new_horse_shoeing_service_instance)
    if res:
        msg = f'horse shoeing service attached to club {club_id}, res : {res.inserted_id}'
        log.info(msg)
        return msg


def get_horse_shoeing_service_by_club_id_logic(club_id):
    res = get_existing_horse_shoeing_service_for_club(club_id)
    if not res:
        raise HTTPException(status_code = 404, detail = f'no riding lesson service found for club {club_id}')
    return res


def attach_trainers_to_riding_service_of_club_logic(club_id, trainers = None):
    if trainers is None:
        trainers = list()
    log.info(f'attach_trainers_to_riding_service_of_club_logic {club_id}, {trainers}')
    res = add_trainers_to_riding_service(club_id, trainers)
    return res


def book_horse_shoeing_service(riding_lesson_instance: BookRidinglessonRequest):
    log.info(f'creating a booking for horse riding lesson, {riding_lesson_instance}')
    # Fetch the corresponding data from the collections
    lesson = riding_lesson_collection.find_one({"_id": ObjectId(riding_lesson_instance.lesson_service)})
    if not lesson:
        raise HTTPException(status_code = 404, detail = "Lesson service not found")

    club_id = lesson['provider']['provider_id']
    club = clubs_collection.find_one({"_id": ObjectId(club_id)})
    if not club:
        raise HTTPException(status_code = 404, detail = "provider club not found")

    rider = users_collection.find_one({"_id": ObjectId(riding_lesson_instance.rider)})
    if not rider:
        raise HTTPException(status_code = 404, detail = "Rider not found")

    trainer = users_collection.find_one({"_id": ObjectId(riding_lesson_instance.trainer)})
    if not trainer:
        raise HTTPException(status_code = 404, detail = "Trainer not found")

    # Create the RidingLessonBooking instance
    booking = RidingLessonBooking(
        lesson_service = RidingLessonService(**lesson),
        rider = UserExternal(**rider),
        trainer = UserExternal(**trainer),
        lesson_datetime = riding_lesson_instance.lesson_datetime,
        venue = request.venue if riding_lesson_instance.venue else club['address'],
        payment_status = riding_lesson_instance.payment_status,
        booking_status = riding_lesson_instance.booking_status
    )

    # Insert the booking into the RidingLessonBooking collection
    try:
        result = riding_lesson_bookings_collection.insert_one(booking.model_dump())
        return {"id": str(result.inserted_id)}
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = e)


def update_horse_shoeing_service_by_club_id_logic(club_id: str, updated_club: UpdateClubRequest):
    # Convert the updated_club from pydantic model to dictionary
    updated_horse_shoeing_service_instance = updated_club.model_dump(exclude_none = True).get('horse_shoeing_service', None)
    if not updated_horse_shoeing_service_instance:
        return True

    # get the horse shoeing service associated with club
    existing_horse_shoeing_service = get_existing_horse_shoeing_service_for_club(club_id = club_id)

    updated_riding_lesson_service_request = HorseShoeingService(
        pricing_options = updated_horse_shoeing_service_instance['pricing_options'] if 'pricing_options' in updated_horse_shoeing_service_instance and updated_horse_shoeing_service_instance['pricing_options'] else existing_horse_shoeing_service['pricing_options'],
        provider = updated_horse_shoeing_service_instance['provider'] if 'provider' in updated_horse_shoeing_service_instance and updated_horse_shoeing_service_instance['provider'] else existing_horse_shoeing_service['provider'],
    )

    # Update the club in the database
    result = update_horse_shoeing_service(horse_shoeing_service_id = existing_horse_shoeing_service['id'], updated_horse_shoeing_service_instance = updated_riding_lesson_service_request.model_dump())
    return result.modified_count == 1


