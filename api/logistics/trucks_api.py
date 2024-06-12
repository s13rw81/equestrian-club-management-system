"""
it is understood that Admin i.e the Truck company
already has signed up. So we would by default have a company_collection
available with us.
we need a truck collection.
company_collection will have a reference field 
"""

from typing import List

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from data.dbapis.truck.read_queries import get_trucks_company_by_id
from data.dbapis.truck.write_queries import add_truck_db
from logging_config import log
from models.truck import TruckInternal

from .models import AddTruck, AddTruckResponse, ViewTruckResponse

trucks_api_router = APIRouter(prefix="/trucks", tags=["logistics"])

# TODO
# 1. Add Depends on admin auth
# 2. Reference the Updated company model


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


@trucks_api_router.get("/trucks", response_model_by_alias=False)
def view_truck_list(company_id: str) -> List[ViewTruckResponse]:
    log.info(f"/trucks invoked : company_id {company_id}")

    trucks_list = get_trucks_company_by_id(
        company_id=company_id, fields=["name", "availability"]
    )

    return trucks_list
