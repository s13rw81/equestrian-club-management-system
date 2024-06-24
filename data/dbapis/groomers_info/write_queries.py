from data.db import get_groomers_info_collection
from logging_config import log
from models.groomers import GroomersInfoInternal

groomers_info_collection = get_groomers_info_collection()


def save_groomers_info_db(groomers_info: GroomersInfoInternal) -> str:
    """saves the new groomers information in the database and returns the id

    Args:
        groomers_info (GroomersInfoInternal)

    Returns:
        str: id
    """
    log.info(f"save_groomers_info_db invoked : {groomers_info}")
    groomers_info_id = (
        groomers_info_collection.insert_one(groomers_info.model_dump())
    ).inserted_id

    retval = str(groomers_info_id)

    log.info(f"returning {retval}")

    return retval
