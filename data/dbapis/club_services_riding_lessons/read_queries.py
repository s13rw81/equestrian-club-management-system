from data.db import get_riding_lesson_collection, get_riding_lesson_bookings_collection
from fastapi import HTTPException, status

riding_lesson_collection = get_riding_lesson_collection()
riding_lesson_bookings_collection = get_riding_lesson_bookings_collection()


def get_existing_riding_lesson_service_for_club(club_id):
    res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


# def get_existing_riding_lesson_service_for_club(club_id: str) -> bool:
#     res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
#     return res
def get_existing_riding_lesson_service_bookings():
    res = riding_lesson_bookings_collection.find({})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


# def get_existing_riding_lesson_service_for_club(club_id: str) -> bool:
#     res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
#     return res

def get_existing_riding_lesson_service_by_user_id(user_id):
    res = riding_lesson_collection.find_one({'provider.provider_id': user_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


def get_existing_riding_lesson_service_booking_by_user_id(user_id):
    res = riding_lesson_bookings_collection.find({'user_id': user_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


def get_riding_lesson_service_bookings_by_riding_lesson_id(riding_lesson_id: str) -> bool:
    res = riding_lesson_bookings_collection.find({'riding_lesson_service_id': riding_lesson_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval
