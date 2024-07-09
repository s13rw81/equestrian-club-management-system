from data.db import convert_to_object_id, get_horse_renting_service_collection
from logging_config import log
from models.horse.horse_renting_service_internal import (
    HorseRentingServiceInternalWithID,
)

renting_service_collection = get_horse_renting_service_collection()


def get_renting_service_details_by_service_id(
    service_id: str,
) -> HorseRentingServiceInternalWithID:
    """based on service_id of horse renting service return the horse renting service details

    Args:
        service_id (str)

    Returns:
        HorseRentingServiceInternalWithID
    """

    log.info(
        f"get_renting_service_details_by_service_id() invoked service_id {service_id}"
    )

    filter = {"_id": convert_to_object_id(service_id)}
    response = renting_service_collection.find_one(filter=filter)

    renting_service_details = HorseRentingServiceInternalWithID(**response)

    log.info(
        f"get_renting_service_details_by_service_id() returning {renting_service_details}"
    )

    return renting_service_details
