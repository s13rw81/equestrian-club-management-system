from data.db import get_riding_lesson_collection
from fastapi import HTTPException, status

riding_lesson_collection = get_riding_lesson_collection()


def insert_riding_instance_to_club(riding_lesson_service_instance):
    res = riding_lesson_collection.insert_one(riding_lesson_service_instance.model_dump())
    return res


def get_riding_lesson_by_club_id(club_id):
    res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    res['id'] = str(res['_id'])
    del(res['_id'])
    return res


def add_trainers_to_riding_service(club_id, trainers):
    riding_service_of_club = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    if riding_service_of_club:
        res = riding_lesson_collection.update_one({'provider.provider_id': club_id}, {'$push': {'trainers': {'$each': trainers}}})
        return res.modified_count == 1
    else:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'riding service for club {club_id} not found.')


def check_existing_riding_service_for_club(club_id: str):
    res = riding_lesson_collection.find_one({'provider.provider_id': club_id})
    if not res:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail='riding service for club already exists.')
    return True
