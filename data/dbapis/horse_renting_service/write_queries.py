from typing import Dict, List

from data.db import convert_to_object_id, get_horse_renting_service_collection
from logging_config import log
from models.horse.horse_renting_service_internal import HorseRentingServiceInternal

horse_renting_service_collection = get_horse_renting_service_collection()


def add_horse_renting_service_details(
    renting_service_details: HorseRentingServiceInternal,
) -> str:
    """given a horse_id create an entry for the horse in horse_renting_service collection and
    return the service_id

    Args:
        horse_id (str)
        renting_service_details (HorseRentingServiceInternal)

    Returns:
        str: id of the horse renting service
    """

    log.info(
        f"add_horse_renting_service_details() invoked renting_service_details {renting_service_details}"
    )

    renting_service_id = (
        horse_renting_service_collection.insert_one(
            renting_service_details.model_dump()
        )
    ).inserted_id

    log.info(f"add_horse_renting_service_details() returning {renting_service_id}")

    return str(renting_service_id)


def update_renting_service_images(service_id: str, image_ids: List[str]) -> bool:
    """given a list of image id update the same to horse_renting_service collection

    Args:
        service_id (str)
        image_ids (List[str])
    """

    log.info(f"update_club_to_club_service_images() invoked : truck_id {service_id}")

    update = {"$set": {"images": image_ids}}

    filter = {"_id": convert_to_object_id(service_id)}
    updated = horse_renting_service_collection.update_one(filter=filter, update=update)

    return updated.modified_count == 1


def update_horse_renting_service_details(service_id: str, update_details: Dict) -> bool:
    """given a service_id and update_details update the renting service details in the database

    Args:
        service_id (str)
        update_details (Dict)

    Returns:
        bool
    """

    log.info(
        f"update_horse_renting_service_details() invoked service_id {service_id}, update_details {update_details}"
    )

    filter = {"_id": convert_to_object_id(service_id)}
    update = {k: v for k, v in update_details.items() if v != None and k != "_id"}

    if not update:
        return False

    update_response = horse_renting_service_collection.update_one(
        filter=filter, update={"$set": update}
    )

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
