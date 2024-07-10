from typing import Dict

from data.db import convert_to_object_id, get_horse_collection
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


def update_horse(horse_id: str, update_details: Dict) -> str:
    """update the corresponding details of the horse_id

    Args:
        horse_details (Dict)

    Returns:
        bool
    """

    filter = {"_id": convert_to_object_id(horse_id)}
    update = {
        k: v
        for k, v in update_details.items()
        if v != None and k not in ("_id", "price")
    }
    # we don't want to include the price in the horse collection

    if not update:
        return False

    update_response = horse_collection.update_one(
        filter=filter, update={"$set": update}
    )

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
