from fastapi import APIRouter

from .horse_renting_service_api import horse_renting_service_router

horse_trade_services_router = APIRouter(prefix="/user/horses", tags=["user-horses"])

horse_trade_services_router.include_router(horse_renting_service_router)
