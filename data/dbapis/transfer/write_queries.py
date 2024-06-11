from api.logistics.models import UpdateTransferStatus
from data.db import convert_to_object_id, get_transfer_collection
from logging_config import log
from models.transfer import TransfersInternal

transfer_collection = get_transfer_collection()


def save_transfer_db(transfer: TransfersInternal) -> str:
    """saves the new transfer in the database and returns the id

    Args:
        transfer (TransfersInternal)
    Returns:
        str: id
    """

    log.info(f"save_transfer invoked : {transfer}")
    transfer_id = (transfer_collection.insert_one(transfer.model_dump())).inserted_id

    retval = str(transfer_id)

    log.info(f"returning {retval}")

    return retval


def update_transfer_status_db(transfer_id: str, body: UpdateTransferStatus) -> str:
    """updates the transfer status in the database for the provided transfer_id
    and returns the transfer_id

    Args:
        transfer_id (str): transfer to update
        status (TransferStatus): status to update

    Returns:
        str: transfer_id
    """

    log.info(
        f"update_transfer_status_db invoked : transfer_id {transfer_id}, status{body}"
    )

    update_response = transfer_collection.update_one(
        filter={"_id": convert_to_object_id(transfer_id)},
        update={"$set": {"status": body.status.value, "updated_at": body.updated_at}},
    )

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
