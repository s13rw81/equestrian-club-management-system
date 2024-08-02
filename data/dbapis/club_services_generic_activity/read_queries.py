from data.db import get_generic_activity_service_collection

generic_activity_service_collection = get_generic_activity_service_collection()


def get_existing_generic_activity_service_for_club(club_id: str):
    res = generic_activity_service_collection.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del(res['_id'])
    return res
