from data.db import get_horse_collection
from logging_config import log
from models.horse.horse import HorseInternal

horse_collection = get_horse_collection()


def add_horse(horse_details: HorseInternal) -> str:
    """add horse details to the horse collection and return the horse_id

    Args:
        horse_details (HorseInternal)

    Returns:
        str: id of the horse added
    """

    log.info(f"add_horse() invoked horse_details {horse_details}")

    horse_id = (
        horse_collection.insert_one(document=horse_details.model_dump())
    ).inserted_id

    log.info(f"add_horse() returning horse_id {horse_id}")

    return str(horse_id)
