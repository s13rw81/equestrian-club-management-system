from typing import List

from api.riding_lesson_services.models.book_riding_lesson_request_model import BookRidinglessonRequest
from fastapi import APIRouter
from logging_config import log
from logic.riding_lesson_services.riding_lesson_service_logic import attach_riding_lesson_to_club_logic, \
    get_riding_lesson_by_club_id_logic, attach_trainers_to_riding_service_of_club_logic, book_horse_riding_lesson

riding_lesson_services_api_router = APIRouter(prefix="/riding-lesson-services", tags=["riding lesson services"])


@riding_lesson_services_api_router.post('/')
async def create_riding_lesson_service_for_club(club_id, price, description=None):
    log.info(f"attaching riding lesson to club with id {club_id} and price: {price} and description: {description}")
    res = attach_riding_lesson_to_club_logic(club_id=club_id, price=price, description=description)
    return {'status_code': 201, 'detail': res['acknowledged']}


@riding_lesson_services_api_router.get('/')
async def get_riding_lesson_by_club_id(club_id: str) -> dict:
    log.info(f"fetching riding lesson by club id {club_id}")
    res = get_riding_lesson_by_club_id_logic(club_id)
    return {'status_code': 200, 'detail': 'OK', 'data': res}


@riding_lesson_services_api_router.post('/attach-trainer-to-riding-lesson-service')
async def atach_trainer_to_riding_service_of_club(club_id: str, trainers: List[str]) -> dict:
    log.info(f"attaching trainers to riding service of club with id {club_id}, trainer ids : {trainers}")
    res = attach_trainers_to_riding_service_of_club_logic(club_id, trainers)
    return {'status_code': 200, 'detail': 'OK', 'data': res}


@riding_lesson_services_api_router.post('/book_riding_lesson')
async def create_riding_lesson_booking(riding_lesson_instance: BookRidinglessonRequest):
    log.info(f'creating a booking for horse riding lesson, {riding_lesson_instance}')
    res = book_horse_riding_lesson(riding_lesson_instance)
    if res:
        return {'status_code': 201, 'detail': 'riding lesson booking created', 'data': res}
