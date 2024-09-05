from typing import Annotated, List

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from pydantic_extra_types.coordinate import Latitude, Longitude

from data.dbapis.truck.read_queries import (
    get_all_trucks,
    get_truck_details_by_id_db,
    get_trucks_by_logistics_company_id,
)
from data.dbapis.truck.write_queries import (
    add_truck_db,
    update_truck_details,
    update_truck_images,
)
from logging_config import log
from logic.logistics.haversine import haversine
from models.truck.trucks import TruckInternal
from utils.image_management import generate_image_urls, save_image

from .api_validators.logistics_company_trucks import (
    AddTruckValidator,
    FindNearbyTrucksValidator,
    GetTrucksValidator,
    GetTruckValidator,
    UpdateTruckDetailsValidator,
    UploadTruckImagesValidator,
)
from .models import (
    AddTruckResponse,
    ResponseTruckDetails,
    ResponseViewTruck,
    TruckDetails,
    ViewTruck,
)

trucks_router = APIRouter(prefix="/trucks", tags=["logistic-company"])
user_trucks_router = APIRouter(tags=["users-logistics"])


@trucks_router.post("/add-truck")
def add_truck(
    request: Request,
    payload: Annotated[AddTruckValidator, Depends()],
) -> AddTruckResponse:

    truck_details = payload.add_truck
    logistics_company_id = payload.logistics_company_id

    log.info(f"{request.url.path} invoked : truck_details {payload.add_truck}")

    truck = TruckInternal(
        registration_number=truck_details.registration_number,
        truck_type=truck_details.truck_type,
        capacity=truck_details.capacity,
        special_features=truck_details.special_features,
        gps_equipped=truck_details.gps_equipped,
        air_conditioning=truck_details.air_conditioning,
        logistics_company_id=logistics_company_id,
        name=truck_details.name,
        driver=truck_details.driver,
        location=truck_details.location,
        # services=truck_details.services,
    )

    log.info(f"truck {truck}")

    updated, truck_id = add_truck_db(truck=truck)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to save truck.",
        )

    response = AddTruckResponse(truck_id=truck_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@trucks_router.get("/get-truck", response_model=List[ResponseViewTruck])
def get_trucks(request: Request, payload: Annotated[GetTrucksValidator, Depends()]):

    logistics_company_id = payload.logistics_company_id

    log.info(
        f"{request.url.path} invoked : logistics_company_id {logistics_company_id}"
    )

    trucks_list = get_trucks_by_logistics_company_id(
        logistics_company_id=logistics_company_id,
        fields=[
            "logistics_company_id",
            "registration_number",
            "truck_type",
            "capacity",
            "special_features",
            "gps_equipped",
            "air_conditioning",
            "name",
            "truck_id",
            "driver",
            "location",
            "images",
        ],
    )

    trucks = [ViewTruck(**truck) for truck in trucks_list]

    for truck in trucks:
        if truck.image_urls:
            truck.image_urls = generate_image_urls(
                image_ids=truck.image_urls, request=request
            )

    log.info(f"{request.url.path} returning {trucks}")

    return trucks


@trucks_router.get("/get-truck/{truck_id}", response_model=ResponseTruckDetails)
def get_truck(
    payload: Annotated[GetTruckValidator, Depends()],
    request: Request,
):

    truck_id = payload.truck_id

    log.info(f"{request.url.path} invoked : truck_id {truck_id}")

    truck = get_truck_details_by_id_db(
        truck_id=truck_id,
        fields=[
            "logistics_company_id",
            "registration_number",
            "truck_type",
            "capacity",
            "special_features",
            "gps_equipped",
            "air_conditioning",
            "name",
            "truck_id",
            "driver",
            "location",
            "images",
        ],
    )

    if not truck:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid truck id provided"
        )

    truck_details = TruckDetails(**truck)

    if truck_details.image_urls:
        truck_details.image_urls = generate_image_urls(
            image_ids=truck_details.image_urls, request=request
        )

    log.info(f"{request.url.path} returning : {truck_details}")

    return truck_details


@trucks_router.post("/upload-truck-images/{truck_id}")
async def upload_truck_images(
    request: Request,
    payload: Annotated[UploadTruckImagesValidator, Depends()],
):
    truck_id = payload.truck_id
    user = payload.user
    files = payload.files

    log.info(f"{request.url.path} invoked : truck_id {truck_id}")

    image_ids = []
    for file in files:
        image_id = await save_image(image_file=file)
        image_ids.append(image_id)

    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_truck_images(truck_id=truck_id, image_ids=image_ids)

    return {"status": "OK"}


@trucks_router.put("/update-truck/{truck_id}")
def update_truck(
    payload: Annotated[UpdateTruckDetailsValidator, Depends()], request: Request
):

    update_details = payload.update_details
    truck_id = payload.truck_id

    log.info(f"{request.url.path} invoked : update_details {update_details}")

    update_truck_details(truck_id=truck_id, truck_details=update_details)

    return {"status": "OK"}


@user_trucks_router.get("/find-nearby-trucks", response_model=List[ResponseViewTruck])
def find_nearby_trucks(
    payload: Annotated[FindNearbyTrucksValidator, Depends()], request: Request
):

    radius = payload.radius
    lat = payload.lat
    long = payload.long

    log.info(f"{request.url.path} invoked radius {radius}, lat {lat}, long {long}")

    fields = [
        "logistics_company_id",
        "registration_number",
        "truck_type",
        "capacity",
        "special_features",
        "gps_equipped",
        "air_conditioning",
        "name",
        "truck_id",
        "driver",
        "location",
        "images",
    ]
    all_trucks = get_all_trucks(fields=fields)

    nearby_trucks = []

    for truck in all_trucks:
        truck_lat = truck["location"]["lat"]
        truck_long = truck["location"]["long"]

        distance = haversine(lon1=long, lat1=lat, lon2=truck_long, lat2=truck_lat)
        log.info(f"distance {distance}")
        if distance <= radius:
            if truck.get("images"):
                truck["images"] = generate_image_urls(
                    image_ids=truck["images"], request=request
                )
            nearby_trucks.append(ViewTruck(**truck))

    log.info(f"{request.url.path} returning {nearby_trucks}")

    return nearby_trucks
