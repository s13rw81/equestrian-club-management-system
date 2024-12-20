from fastapi import APIRouter

from .logistics_company_services_api import manage_service_router
from .logistics_company_trucks_api import trucks_router, user_trucks_router
from .logistics_user_service_booking_api import user_service_booking_router

logistics_admin_router = APIRouter(
    prefix="/logistic-company", tags=["logistic-company"]
)

logistics_user_router = APIRouter(prefix="/user/logistics", tags=["users-logistics"])


logistics_admin_router.include_router(trucks_router)
logistics_admin_router.include_router(manage_service_router)

logistics_user_router.include_router(user_trucks_router)
logistics_user_router.include_router(user_service_booking_router)
