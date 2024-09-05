from bson import ObjectId
from data.db import get_horse_shoeing_service_collection
from data.db import get_horse_shoeing_service_bookings_collection

horse_shoeing_service_collection = get_horse_shoeing_service_collection()
horse_shoeing_bookings_collection = get_horse_shoeing_service_bookings_collection()


def insert_horse_shoeing_instance_to_club(new_horse_shoeing_service_instance):
    res = horse_shoeing_service_collection.insert_one(new_horse_shoeing_service_instance.model_dump())
    # return res.inserted_id
    return res


def add_ferrier_to_horse_shoeing_service(club_id, trainers):
    riding_service_of_club = horse_shoeing_service_collection.find_one({'provider.provider_id': club_id})
    if riding_service_of_club:
        res = horse_shoeing_service_collection.update_one({'provider.provider_id': club_id},
                                                          {'$push': {'trainers': {'$each': trainers}}})
        return res.modified_count == 1
    return riding_service_of_club


def update_horse_shoeing_service(horse_shoeing_service_id, updated_horse_shoeing_service_instance):
    return horse_shoeing_service_collection.update_one({'_id': ObjectId(horse_shoeing_service_id)},
                                                       {'$set': updated_horse_shoeing_service_instance})


def create_new_horse_shoeing_service_booking(horse_shoeing_service_booking: dict):
    # Insert the booking into the RidingLessonBooking collection
    result = horse_shoeing_bookings_collection.insert_one(horse_shoeing_service_booking)
    return result
