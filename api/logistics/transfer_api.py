from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from data.dbapis.transfer.write_queries import save_transfer
from logging_config import log
from logic.auth import get_current_user
from models.transfer import TransfersInternal
from models.transfer.enums import TransferStatus
from models.user import UserInternal

from .models import CreateTransfer, ResponseCreateTransfer

logistics_api_router = APIRouter(prefix="/logistics", tags=["logistics"])


@logistics_api_router.post("/transfers")
def create_transfer(
    create_transfer: CreateTransfer,
    user: Annotated[UserInternal, Depends(get_current_user)],
) -> ResponseCreateTransfer:

    log.info(f"create_transfer {create_transfer}")

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

    transfer_id = save_transfer(transfer=transfer)

    if not transfer_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    return ResponseCreateTransfer(
        transfer_id=transfer_id,
        status=transfer_status,
        message="Transfer created Successfully.",
    )
