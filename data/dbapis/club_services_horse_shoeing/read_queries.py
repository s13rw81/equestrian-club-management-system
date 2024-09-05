from data.db import get_horse_shoeing_service_collection, get_horse_shoeing_service_bookings_collection

horse_shoeing_service = get_horse_shoeing_service_collection()
horse_shoeing_service_bookings = get_horse_shoeing_service_bookings_collection()


def get_existing_horse_shoeing_service_for_club(club_id):
    res = horse_shoeing_service.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


def get_existing_horse_shoeing_service_bookings_for_club(horse_shoeing_service_id):
    res = horse_shoeing_service_bookings.find({'horse_shoeing_service_id': horse_shoeing_service_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


#
# def get_existing_horse_shoeing_service_for_club(club_id: str) -> bool:
#     res = services_horse_shoeing.find_one({'provider.provider_id': club_id})
#     return res

def get_existing_horse_shoeing_service_by_user_id(user_id: str):
    res = horse_shoeing_service.find_one({'user_id': user_id})
    if res:
        res['id'] = str(res['_id'])
        del (res['_id'])
    return res


def get_existing_horse_shoeing_service_bookings_by_user_id(user_id: str):
    res = horse_shoeing_service_bookings.find({'user_id': user_id})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


def get_all_existing_horse_shoeing_service():
    res = horse_shoeing_service.find({})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval


def get_all_existing_horse_shoeing_service_bookings():
    res = horse_shoeing_service_bookings.find({})
    retval = list()
    if res:
        for r in res:
            r['id'] = str(r['_id'])
            del (r['_id'])
            retval.append(r)
    return retval
