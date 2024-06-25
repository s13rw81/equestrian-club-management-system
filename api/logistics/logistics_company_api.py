from typing import List

from fastapi import APIRouter, File, Request, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from data.dbapis.logistics_company_services.read_queries import (
    club_to_club_service_by_logistics_company_id,
    get_club_to_club_service_by_service_id,
    get_logistics_company_by_id,
)
from data.dbapis.logistics_company_services.write_queries import (
    save_club_to_club_service_db,
    update_club_to_club_service,
)
from data.dbapis.truck.read_queries import (
    get_truck_details_by_id_db,
    get_trucks_by_logistics_company_id,
)
from data.dbapis.truck.write_queries import (
    add_truck_db,
    update_truck_availability,
    update_truck_images,
)
from logging_config import log
from logic.logistics.write_truck_images import write_images
from models.logistics_company_services import (
    ClubToClubServiceInternal,
    Provider,
    UserTransferServiceInternal,
    UserTransferServiceWithInsuranceInternal,
)
from models.logistics_company_services.enums.service_enums import ServiceAvailability
from models.truck.trucks import TruckInternal

from .models import (
    AddClubToClubService,
    AddTruck,
    AddTruckResponse,
    ResponseAddClubToClubService,
    ResponseGetClubToClubService,
    ResponseTruckDetails,
    UpdateClubToClubService,
    UpdateTruckDetails,
    UploadTruckImages,
    ViewTruckResponse,
)

logistics_company_api_router = APIRouter(
    prefix="/logistic-company",
    tags=["logistic-company"],
)


@logistics_company_api_router.post("/trucks/add-truck")
def add_truck(truck_details: AddTruck, request: Request) -> AddTruckResponse:

    log.info(f"{request.url.path} invoked : truck_details {truck_details}")

    truck = TruckInternal(
        registration_number=truck_details.registration_number,
        truck_type=truck_details.truck_type,
        capacity=truck_details.capacity,
        special_features=truck_details.special_features,
        gps_equipped=truck_details.gps_equipped,
        air_conditioning=truck_details.air_conditioning,
        logistics_company_id=truck_details.logistics_company_id,
        name=truck_details.name,
        services=truck_details.services,
    )

    log.info(f"truck {truck}")

    updated, truck_id = add_truck_db(truck=truck)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to save truck.",
        )

    response = AddTruckResponse(
        success=updated, truck_id=truck_id, message="Truck successfully added"
    )

    log.info(f"{request.url.path} returning {response}")

    return response


@logistics_company_api_router.get(
    "/trucks/get-trucks/{logistics_company_id}", response_model_by_alias=False
)
def get_trucks(logistics_company_id: str, request: Request) -> List[ViewTruckResponse]:
    log.info(
        f"{request.url.path} invoked : logistics_company_id {logistics_company_id}"
    )

    trucks_list = get_trucks_by_logistics_company_id(
        logistics_company_id=logistics_company_id,
        fields=[
            "name",
            "availability",
            "logistics_company_id",
            "capacity",
            "registration_number",
        ],
    )

    return trucks_list


@logistics_company_api_router.get(
    "/trucks/get-truck/{truck_id}", response_model_by_alias=False
)
def get_truck(truck_id: str, request: Request) -> ResponseTruckDetails:
    log.info(f"{request.url.path} invoked : truck_id {truck_id}")

    truck_details = get_truck_details_by_id_db(
        truck_id=truck_id,
        fields=[
            "name",
            "truck_type",
            "availability",
            "images",
            "logistics_company_id",
            "registration_number",
        ],
    )

    log.info(f"{request.url.path} returning : {truck_details}")

    return truck_details


@logistics_company_api_router.post("/trucks/{truck_id}/images")
def upload_truck_images(
    truck_id: str,
    request: Request,
    truck_descriptions: UploadTruckImages,
    files: List[UploadFile] = File(...),
):

    log.info(f"{request.url.path} invoked : truck_id {truck_id}")

    if len(truck_descriptions.description) != len(files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="truck images and descriptions are required",
        )

    file_paths = write_images(truck_id=truck_id, files=files)

    if not file_paths:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_truck_images(
        truck_id=truck_id,
        file_paths=file_paths,
        description=truck_descriptions.description,
    )

    return {"message": "Images uploaded successfully"}


@logistics_company_api_router.put("/trucks/update-truck/{truck_id}")
def update_truck(update_details: UpdateTruckDetails, request: Request):

    log.info(f"{request.url.path} invoked : update_details {update_details}")

    update_truck_availability(
        truck_id=update_details.truck_id, availability=update_details.availability.value
    )

    return {"message": "Truck availability updated successfully"}


@logistics_company_api_router.get(
    "/services/get-club-to-club-service/{logistics_company_id}"
)
def get_club_to_club_transfer_service(
    logistics_company_id: str, request: Request
) -> ResponseGetClubToClubService:

    log.info(f"{request.url.path} invoked")

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

    log.info(f"{request.url.path} returning : {response}")

    return response


@logistics_company_api_router.post("/services/add-club-to-club-service")
def add_club_to_club_transfer_service(
    club_to_club_service_details: AddClubToClubService, request: Request
) -> ResponseAddClubToClubService:

    log.info(f"{request.url.path} invoked : {club_to_club_service_details}")

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

    log.info(f"{request.url.path} returning : {response}")

    return response


@logistics_company_api_router.put("/services/update-club-to-club-service/{service_id}")
def update_club_to_club_transfer_service(
    service_id: str, service_update_details: UpdateClubToClubService, request: Request
):

    log.info(f"{request.url.path} invoked : {service_update_details}")

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
