from fastapi import APIRouter

from .logistics_company_services_api import manage_service_router
from .logistics_company_trucks_api import trucks_router
from .logistics_services_booking_api import service_booking_router

logistics_admin_router = APIRouter(
    prefix="/logistic-company", tags=["logistic-company"]
)

logistics_user_router = APIRouter(prefix="/logistics", tags=["logistics-user"])


logistics_admin_router.include_router(trucks_router)
logistics_admin_router.include_router(manage_service_router)

logistics_user_router.include_router(service_booking_router)
