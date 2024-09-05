from data.db import get_generic_activity_service_collection, get_generic_activity_service_bookings_collection

generic_activity_service_collection = get_generic_activity_service_collection()
generic_activity_service_bookings_collection = get_generic_activity_service_bookings_collection()


def get_existing_generic_activity_service_for_club(club_id: str):
    res = generic_activity_service_collection.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


def get_all_existing_generic_activity_service_bookings_for_club(generic_activity_service_id: str):
    res = generic_activity_service_bookings_collection.find({'generic_activity_service_id': generic_activity_service_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


def get_existing_generic_activity_service_by_user_id(user_id: str):
    res = generic_activity_service_collection.find_one({'user_id': user_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


def get_existing_generic_activity_service_bookings_by_user_id(user_id: str):
    res = generic_activity_service_bookings_collection.find({'user_id': user_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


def get_all_existing_generic_activity_service():
    res = generic_activity_service_collection.find({})
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
    return res


def get_all_existing_generic_activity_service_bookings():
    res = generic_activity_service_bookings_collection.find({})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval
