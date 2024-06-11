from data.db import convert_to_object_id, get_transfer_collection
from logging_config import log
from models.transfer import TransfersInternal

transfer_collection = get_transfer_collection()


def get_transfer_by_object_id(transfer_id: str) -> str:
    """fetch transfer details from database for the provided id

    Args:
        transfer_id (str): id of the transfer to fetch

    Returns:
        TransfersInternal: transfer_details
    """

    transfer_details = transfer_collection.find_one(
        filter={"_id": convert_to_object_id(transfer_id)}
    )

    return transfer_details
