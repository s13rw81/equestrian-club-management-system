from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from data.dbapis.groomers_info.write_queries import save_groomers_info_db
from data.dbapis.horse_profiles.write_queries import save_horse_profile_db
from data.dbapis.transfer.read_queries import get_transfer_by_object_id
from data.dbapis.transfer.write_queries import (
    save_customer_transfer_db,
    save_transfer_db,
    update_transfer_status_db,
)
from data.dbapis.truck.read_queries import get_truck_details_by_id_db
from data.dbapis.truck.write_queries import update_truck_availability
from logging_config import log
from logic.auth import get_current_user
from logic.logistics.status_validation import validate_update_status
from models.groomers import GroomersInfoInternal
from models.horse_profiles import HorseProfileInternal
from models.transfer import (
    CustomersTransfersInternal,
    TransfersInternal,
    TransfersInternalWithID,
)
from models.transfer.enums import TransferStatus
from models.truck.enums import TruckAvailability
from models.user import UserInternal

from .models import (
    CreateCustomerTransfer,
    CreateTransfer,
    GroomersInfo,
    HorseProfile,
    ResponseCreateCustomerTransfer,
    ResponseCreateTransfer,
    ResponseGroomersInfo,
    ResponseHorseProfile,
    ResponseUpdateTransferStatus,
    UpdateTransferStatus,
)

transfer_api_router = APIRouter(prefix="/transfers", tags=["logistics"])


@transfer_api_router.post("")
def create_transfer(
    create_transfer: CreateTransfer,
    user: Annotated[UserInternal, Depends(get_current_user)],
) -> ResponseCreateTransfer:

    log.info(f"/transfers invoked : {create_transfer}")

    truck_details = get_truck_details_by_id_db(
        truck_id=create_customer_transfer.truck_id,
        fields=["company_id", "availability"],
    )

    truck_available = truck_details.get("availability") == TruckAvailability.AVAILABLE
    if not truck_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selected truck is not currently available",
        )

    transfer_status = TransferStatus.CREATED

    transfer = TransfersInternal(
        customer_id=create_transfer.customer_id,
        horse_id=create_transfer.horse_id,
        source_club_id=create_transfer.source_club_id,
        destination_club_id=create_transfer.destination_club_id,
        logistics_company_id=create_transfer.logistics_company_id,
        truck_id=create_transfer.truck_id,
        pickup_time=create_transfer.pickup_time,
        status=transfer_status,
    )

    transfer_id = save_transfer_db(transfer=transfer)

    truck_availability_updated = update_truck_availability(
        truck_id=create_transfer.truck_id,
        availability=TruckAvailability.UN_AVAILABLE.value,
    )

    if not transfer_id or not truck_availability_updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    response = ResponseCreateTransfer(
        transfer_id=transfer_id,
        status=transfer_status,
        message="Transfer created Successfully.",
    )

    log.info(f"/transfers returning : {response}")

    return response


@transfer_api_router.post("/request")
def create_customer_transfer(
    create_customer_transfer: CreateCustomerTransfer,
) -> ResponseCreateCustomerTransfer:
    log.info(f"/transfers/request invoked : {create_customer_transfer}")

    transfer_status = TransferStatus.CREATED.value

    truck_details = get_truck_details_by_id_db(
        truck_id=create_customer_transfer.truck_id,
        fields=["company_id", "availability"],
    )

    truck_available = (
        truck_details.get("availability") == TruckAvailability.AVAILABLE.value
    )

    if not truck_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selected truck is not currently available",
        )

    customer_transfer = CustomersTransfersInternal(
        customer_id="adsfadsf",
        source_location=create_customer_transfer.source_location,
        destination_location=create_customer_transfer.destination_location,
        truck_id=create_customer_transfer.truck_id,
        logistics_company_id=truck_details.get("company_id"),
        status=transfer_status,
    )

    transfer_id = save_customer_transfer_db(customer_transfer=customer_transfer)

    truck_availability_updated = update_truck_availability(
        truck_id=create_customer_transfer.truck_id,
        availability=TruckAvailability.UN_AVAILABLE.value,
    )

    if not transfer_id or not truck_availability_updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    response = ResponseCreateCustomerTransfer(
        transfer_id=transfer_id,
        status=transfer_status,
    )

    log.info(f"/transfers/request returning : {response}")

    return response


@transfer_api_router.post("/horse/profile")
def add_horse_profile(add_horse_profile: HorseProfile) -> ResponseHorseProfile:
    log.info(
        f"/transfers/horse/profile invoked : add_horse_profile={add_horse_profile}"
    )

    horse_profile = HorseProfileInternal(
        horse_name=add_horse_profile.horse_name,
        customer_transfer_id=add_horse_profile.customer_transfer_id,
        age=add_horse_profile.age,
        health_info=add_horse_profile.health_info,
    )

    horse_profile_id = save_horse_profile_db(horse_profile=horse_profile)

    if not horse_profile_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save horse profile",
        )

    response = ResponseHorseProfile(profile_id=horse_profile_id)

    log.info(f"/transfers/horse/profile returning : {response}")

    return response


@transfer_api_router.post("/groomer/info")
def add_groomer_info(add_groomer_info: GroomersInfo) -> ResponseGroomersInfo:
    log.info(f"/transfers/groomer/info invoked : add_groomer_info={add_groomer_info}")

    groomer_info = GroomersInfoInternal(
        customer_transfer_id=add_groomer_info.customer_transfer_id,
        groomer_name=add_groomer_info.groomer_name,
        contact_number=add_groomer_info.contact_number,
    )

    groomer_info_id = save_groomers_info_db(groomers_info=groomer_info)

    response = ResponseGroomersInfo(info_id=groomer_info_id)

    log.info(f"/transfers/groomer/info returning : {response}")

    return response


@transfer_api_router.patch("/{transfer_id}/status")
def update_transfer_status(
    user: Annotated[UserInternal, Depends(get_current_user)],
    transfer_id: str,
    update_body: UpdateTransferStatus,
) -> ResponseUpdateTransferStatus:

    log.info(f"/transfers/{transfer_id}/status invoked : transfer_status={update_body}")

    valid_update = validate_update_status(
        transfer_id=transfer_id, status_to_update=update_body.status
    )

    if not valid_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provide a valid update status",
        )

    updated = update_transfer_status_db(transfer_id=transfer_id, body=update_body)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to update the status of the transfer",
        )

    response = ResponseUpdateTransferStatus(
        transfer_id=transfer_id,
        status=update_body.status.value,
        message="Transfer status updated successfully",
    )

    log.info(f"/transfer/{transfer_id}/status returning : {response}")

    return response


@transfer_api_router.get("/{transfer_id}")
def get_transfer_details(
    user: Annotated[UserInternal, Depends(get_current_user)], transfer_id: str
) -> TransfersInternalWithID:

    log.info(f"/transfers/{transfer_id} invoked : transfer_id {transfer_id}")

    transfer_details = get_transfer_by_object_id(transfer_id=transfer_id)

    if not transfer_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid transfer_id provided",
        )

    response = TransfersInternalWithID(**transfer_details)

    log.info(f"/transfers/{transfer_id} returning : {response}")

    return response
