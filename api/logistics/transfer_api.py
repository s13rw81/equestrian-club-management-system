from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from data.dbapis.transfer.read_queries import get_transfer_by_object_id
from data.dbapis.transfer.write_queries import (
    save_transfer_db,
    update_transfer_status_db,
)
from logging_config import log
from logic.auth import get_current_user
from logic.logistics.status_validation import validate_update_status
from models.transfer import TransfersInternal, TransfersInternalWithID
from models.transfer.enums import TransferStatus
from models.user import UserInternal

from .models import (
    CreateTransfer,
    ResponseCreateTransfer,
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

    if not transfer_id:
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
