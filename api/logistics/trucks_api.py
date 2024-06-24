"""
it is understood that Admin i.e the Truck company
already has signed up. So we would by default have a company_collection
available with us.
we need a truck collection.
company_collection will have a reference field 
"""

from typing import List

from fastapi import APIRouter, File, UploadFile, status
from fastapi.exceptions import HTTPException

from data.dbapis.truck.read_queries import (
    get_available_trucks_db,
    get_truck_details_by_id_db,
    get_trucks_company_by_id,
)
from data.dbapis.truck.write_queries import (
    add_truck_db,
    update_truck_availability,
    update_truck_images,
)
from logging_config import log
from logic.logistics.write_truck_images import write_images
from models.truck import TruckInternal
from models.truck.enums import TruckAvailability

from .models import (
    AddTruck,
    AddTruckResponse,
    ResponseTruckDetails,
    UploadTruckImages,
    ViewTruckResponse,
)

trucks_api_router = APIRouter(prefix="/trucks", tags=["logistics"])

# TODO
# 1. Add Depends on admin auth
# 2. Reference the Updated company model
# 3. Add validations to all APIs to consider whether logged in user is authorized to manage the truck
# 4. Add exception handling to all apis


@trucks_api_router.post("/add_truck")
def add_truck(truck_details: AddTruck) -> AddTruckResponse:

    log.info(f"/add_truck invoked : {truck_details}")

    truck = TruckInternal(
        truck_type=truck_details.truck_type,
        capacity=truck_details.capacity,
        special_features=truck_details.special_features,
        gps_equipped=truck_details.gps_equipped,
        air_conditioning=truck_details.air_conditioning,
        company_id=truck_details.company_id,
        name=truck_details.name,
    )

    updated, truck_id = add_truck_db(truck=truck)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to save truck.",
        )

    response = AddTruckResponse(
        success=updated, truck_id=truck_id, message="Truck successfully added"
    )

    log.info(f"/add_truck returning {response}")

    return response


@trucks_api_router.get("/", response_model_by_alias=False)
def view_truck_list(company_id: str) -> List[ViewTruckResponse]:
    log.info(f"/trucks invoked : company_id {company_id}")

    trucks_list = get_trucks_company_by_id(
        company_id=company_id, fields=["name", "availability", "company_id"]
    )

    return trucks_list


@trucks_api_router.get("/available", response_model_by_alias=False)
def view_available_trucks(type: str, location: str) -> List[ViewTruckResponse]:
    log.info(f"/trucks/available invoked : {type} location {location}")

    available_trucks_list = get_available_trucks_db(
        type=type,
        location=location,
        fields=["name", "type", "capacity", "availability", "company_id"],
    )

    return available_trucks_list


@trucks_api_router.get("/{truck_id}", response_model_by_alias=False)
def get_truck_details(truck_id: str) -> ResponseTruckDetails:
    log.info(f"/trucks/{truck_id} invoked")

    truck_details = get_truck_details_by_id_db(
        truck_id=truck_id,
        fields=["name", "truck_type", "availability", "images", "company_id"],
    )

    log.info(f"/trucks/{truck_id} returning : {truck_details}")

    return truck_details


@trucks_api_router.post("/{truck_id}/images")
def upload_truck_images(
    truck_id: str,
    truck_descriptions: UploadTruckImages,
    files: List[UploadFile] = File(...),
):

    log.info(f"/{truck_id}/images invoked truck_id {truck_id}")

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


@trucks_api_router.patch("{truck_id}/availability")
def set_truck_availability(truck_id: str, availability: TruckAvailability):
    log.info(f"/trucks/{truck_id}/availability invoked")

    update_truck_availability(truck_id=truck_id, availability=availability.value)

    return {"message": "Truck availability updated successfully"}
