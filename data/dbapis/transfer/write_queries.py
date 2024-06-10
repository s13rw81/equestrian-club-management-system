from data.db import get_transfer_collection
from logging_config import log
from models.transfer import Transfers

transfer_collection = get_transfer_collection()


def save_transfer(transfer: Transfers) -> str:
    """saves the new transfer in the database and returns the id

    Args:
        transfer (Transfers)
    Returns:
        str: id
    """

    log.info(f"save_transfer invoked : {transfer}")
    transfer_id = (transfer_collection.insert_one(transfer.model_dump())).inserted_id

    retval = str(transfer_id)

    log.info(f"returning {retval}")

    return retval
