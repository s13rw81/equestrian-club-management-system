from bson import ObjectId
from data.db import get_riding_lesson_collection, get_riding_lesson_bookings_collection
from logging_config import log

riding_lesson_collection = get_riding_lesson_collection()
riding_lesson_bookings_collection = get_riding_lesson_bookings_collection()


def insert_riding_instance_to_club(riding_lesson_service_instance):
    res = riding_lesson_collection.insert_one(riding_lesson_service_instance.model_dump())
    # return res.inserted_id
    return res


def add_trainers_to_riding_service(club_id, trainers):
    riding_service_of_club = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    if riding_service_of_club:
        res = riding_lesson_collection.update_one({'provider.provider_id': club_id}, {'$push': {'trainers': {'$each': trainers}}})
        return res.modified_count == 1
    return riding_service_of_club


def update_riding_lesson_service(riding_lesson_service_id: str, updated_riding_lesson_service_request: dict):
    return riding_lesson_collection.update_one({'_id': ObjectId(riding_lesson_service_id)}, {'$set': updated_riding_lesson_service_request})


def create_new_riding_lesson_service_booking(riding_lesson_service_booking: dict):
    # Insert the booking into the RidingLessonBooking collection
    result = riding_lesson_bookings_collection.insert_one(riding_lesson_service_booking)
    return result

