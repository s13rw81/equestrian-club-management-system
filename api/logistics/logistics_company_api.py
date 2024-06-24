from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from data.dbapis.logistics.services.read_queries import (
    club_to_club_service_by_logistics_company_id,
    get_club_to_club_service_by_service_id,
    get_logistics_company_by_id,
)
from data.dbapis.logistics.services.write_queries import (
    save_club_to_club_service_db,
    update_club_to_club_service,
)
from logging_config import log
from models.logistics import (
    ClubToClubServiceInternal,
    Provider,
    UserTransferServiceInternal,
    UserTransferServiceWithInsuranceInternal,
)
from models.logistics.enums.service_enums import ServiceAvailability

from .models import (
    AddClubToClubService,
    ResponseAddClubToClubService,
    ResponseGetClubToClubService,
    UpdateClubToClubService,
)

logistics_company_api_router = APIRouter(
    prefix="/logistic-company",
    tags=["logistic-company"],
)


@logistics_company_api_router.get("/get-club-to-club-service/{logistics_company_id}")
def get_club_to_club_transfer_service(
    logistics_company_id: str,
) -> ResponseGetClubToClubService:

    log.info(f"/get-club-to-club-service/{logistics_company_id} invoked")

    service_details = club_to_club_service_by_logistics_company_id(
        logistics_company_id=logistics_company_id
    )
    if not service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the logistic company does not provide this service",
        )

    response = ResponseGetClubToClubService(
        service_id=service_details.service_id,
        logistics_company_id=service_details.provider.provider_id,
        trucks=service_details.trucks,
        created_at=service_details.created_at,
        updated_at=service_details.updated_at,
        is_available=service_details.is_available,
    )

    log.info(f"/get-club-to-club-service/{logistics_company_id} returning : {response}")

    return response


@logistics_company_api_router.post("/add-club-to-club-service")
def add_club_to_club_transfer_service(
    club_to_club_service_details: AddClubToClubService,
) -> ResponseAddClubToClubService:

    log.info(f"/add-club-to-club-service invoked : {club_to_club_service_details}")

    logistics_company_details = get_logistics_company_by_id(
        logistics_company_id=club_to_club_service_details.logistics_company_id
    )
    if not logistics_company_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="logistics company does not exist.",
        )

    service_details = club_to_club_service_by_logistics_company_id(
        logistics_company_id=club_to_club_service_details.logistics_company_id
    )
    if service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="club to club already exists for the logistics company",
        )

    provider = Provider(
        provider_id=club_to_club_service_details.logistics_company_id,
        provider_type="LOGISTICS",
    )
    club_to_club_service = ClubToClubServiceInternal(
        provider=provider, is_available=ServiceAvailability.AVAILABLE
    )

    service_id = save_club_to_club_service_db(service=club_to_club_service)
    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save service",
        )

    response = ResponseAddClubToClubService(service_id=service_id)

    log.info(f"/add-club-to-club-service returning : {response}")

    return response


@logistics_company_api_router.put("/update-club-to-club-service/{service_id}")
def update_club_to_club_transfer_service(
    service_id: str,
    service_update_details: UpdateClubToClubService,
):

    log.info(
        f"/update-club-to-club-service/{service_id} invoked : {service_update_details}"
    )

    service_details = get_club_to_club_service_by_service_id(service_id=service_id)

    if service_details.is_available.value == service_update_details.is_available.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid availability status provided",
        )

    service_updated = update_club_to_club_service(
        service_id=service_id, update_details=service_update_details
    )

    if not service_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to update service",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @logistics_company_api_router.get("/get-user-transfer-service/{service_id}")
# def get_user_transfer_service(): ...


# @logistics_company_api_router.post("/add-user-transfer-service")
# def add_user_transfer_service(): ...


# @logistics_company_api_router.put("/update-user-transfer-service")
# def update_user_transfer_service(): ...


# @logistics_company_api_router.get(
#     "/get-user-luggage-transfer-service-with-insurance/{service_id}"
# )
# def get_user_luggage_transfer_service(): ...


# @logistics_company_api_router.post("/add-user-luggage-transfer-service-with-insurance")
# def add_user_luggage_transfer_service(): ...


# @logistics_company_api_router.put(
#     "/update-user-luggage-transfer-service-with-insurance"
# )
# def update_user_luggage_transfer_service(): ...
