from typing import Union

from data.db import (
    convert_to_object_id,
    get_horse_renting_enquiry_collection,
    get_horse_renting_service_collection,
)
from logging_config import log
from models.horse.horse_renting_service_internal import (
    HorseRentingServiceEnquiryInternalWithID,
    HorseRentingServiceInternalWithID,
)

renting_service_collection = get_horse_renting_service_collection()
renting_enquiry_collection = get_horse_renting_enquiry_collection()


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


def get_renting_enquiry_details_by_user_and_renting_service_id(
    user_id: str, renting_service_id: str
) -> Union[HorseRentingServiceEnquiryInternalWithID, None]:
    """return an enquiry if the enquiry exists based on user_id and renting_service_id

    Args:
        user_id (str)
        renting_service_id (str)

    Returns:
        HorseRentingServiceEnquiryInternalWithID
    """

    log.info(
        f"get_renting_enquiry_details_by_user_and_renting_service_id() invoked user_id {user_id}, renting_service_id {renting_service_id}"
    )

    filter = {"user_id": user_id, "horse_renting_service_id": renting_service_id}

    response = renting_enquiry_collection.find_one(filter=filter)
    if not response:
        return None

    enquiry = HorseRentingServiceEnquiryInternalWithID(**response)

    log.info(
        f"get_renting_enquiry_details_by_user_and_renting_service_id() returning enquiry {enquiry}"
    )

    return enquiry
