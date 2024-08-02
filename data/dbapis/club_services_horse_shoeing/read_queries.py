from data.db import get_horse_shoeing_service_collection

horse_shoeing_service = get_horse_shoeing_service_collection()


def get_existing_horse_shoeing_service_for_club(club_id):
    res = horse_shoeing_service.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del(res['_id'])
    return res

#
# def get_existing_horse_shoeing_service_for_club(club_id: str) -> bool:
#     res = services_horse_shoeing.find_one({'provider.provider_id': club_id})
#     return res
