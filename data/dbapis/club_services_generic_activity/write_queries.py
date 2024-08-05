from bson import ObjectId
from data.db import get_generic_activity_service_collection, get_generic_activity_service_booking_collection

generic_activity_service_collection = get_generic_activity_service_collection()
generic_activity_service_booking_collection = get_generic_activity_service_booking_collection()


def insert_generic_activity_service_instance_to_club(generic_activity_instance):
    res = generic_activity_service_collection.insert_one(generic_activity_instance.model_dump())
    # return res.inserted_id
    return res


def update_generic_activity_service(generic_activity_service_id, updated_generic_activity_service_instance):
    return generic_activity_service_collection.update_one({'_id': ObjectId(generic_activity_service_id)}, {'$set': updated_generic_activity_service_instance})


def create_new_generic_activity_service_booking(booking: dict):
    # Insert the booking into the RidingLessonBooking collection
    result = generic_activity_service_booking_collection.insert_one(booking)
    return result
