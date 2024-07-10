from typing import Dict, List

from api.horses.models import UpdateHorseRentEnquiry
from data.db import (
    convert_to_object_id,
    get_horse_renting_enquiry_collection,
    get_horse_renting_service_collection,
)
from logging_config import log
from models.horse.horse_renting_service_internal import (
    HorseRentingServiceEnquiryInternal,
    HorseRentingServiceInternal,
)

horse_renting_service_collection = get_horse_renting_service_collection()
renting_enquiry_collection = get_horse_renting_enquiry_collection()


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


def add_horse_renting_service_enquiry(
    enquiry_details: HorseRentingServiceEnquiryInternal,
) -> str:
    """add a new enquiry for a horse renting service and return the enquiry id

    Args:
        enquiry_details (HorseRentingServiceEnquiryInternal)

    Returns:
        str: id of the enquiry
    """

    log.info(
        f"add_horse_renting_service_enquiry() invoked enquiry_details {enquiry_details}"
    )

    enquiry_id = (
        renting_enquiry_collection.insert_one(document=enquiry_details.model_dump())
    ).inserted_id

    log.info(f"add_horse_renting_service_enquiry() returning {enquiry_id}")

    return str(enquiry_id)


def update_horse_renting_service_enquiry(
    enquiry_id: str,
    enquiry_details: UpdateHorseRentEnquiry,
) -> str:
    """update the enquiry with enquiry_details of the given enquiry_id

    Args:
        enquiry_details (UpdateHorseRentEnquiry)
    """

    log.info(
        f"update_horse_renting_service_enquiry() invoked enquiry_details {enquiry_details}"
    )

    filter = {"_id": convert_to_object_id(enquiry_id)}
    update = {
        k: v
        for k, v in enquiry_details.model_dump().items()
        if v != None and k != "_id"
    }

    if not update:
        return False

    update_response = renting_enquiry_collection.update_one(
        filter=filter, update={"$set": update}
    )

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
