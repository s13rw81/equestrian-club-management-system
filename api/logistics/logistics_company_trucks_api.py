from typing import List

from fastapi import APIRouter, File, Request, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

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
from models.truck.trucks import TruckInternal

from .models import (
    AddTruck,
    AddTruckResponse,
    ResponseTruckDetails,
    UpdateTruckDetails,
    UploadTruckImages,
    ViewTruckResponse,
)

trucks_router = APIRouter(prefix="/trucks", tags=["logistics-company"])


@trucks_router.post("/add-truck")
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


@trucks_router.get("/get-trucks/{logistics_company_id}", response_model_by_alias=False)
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


@trucks_router.get("/get-truck/{truck_id}", response_model_by_alias=False)
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


@trucks_router.post("/{truck_id}/images")
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


@trucks_router.put("/update-truck/{truck_id}")
def update_truck(update_details: UpdateTruckDetails, request: Request):

    log.info(f"{request.url.path} invoked : update_details {update_details}")

    update_truck_availability(
        truck_id=update_details.truck_id, availability=update_details.availability.value
    )

    return {"message": "Truck availability updated successfully"}
