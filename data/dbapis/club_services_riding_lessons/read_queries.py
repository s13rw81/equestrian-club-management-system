from data.db import get_riding_lesson_collection
from fastapi import HTTPException, status

riding_lesson_collection = get_riding_lesson_collection()


def get_existing_riding_lesson_service_for_club(club_id):
    res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    if res:
        res['id'] = str(res['_id'])
        del(res['_id'])
    return res


# def get_existing_riding_lesson_service_for_club(club_id: str) -> bool:
#     res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
#     return res
