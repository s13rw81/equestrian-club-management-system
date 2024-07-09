from typing import List, Union

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


def get_renting_enquiry_details_by_enquiry_id(
    enquiry_id: str,
) -> Union[HorseRentingServiceEnquiryInternalWithID, None]:
    """return an enquiry if the enquiry exists based on the enquiry id

    Args:
        enquiry_id (str): _description_

    Returns:
        Union[HorseRentingServiceEnquiryInternalWithID, None]
    """

    log.info(
        f"get_renting_enquiry_details_by_enquiry_id() invoked enquiry_id {enquiry_id}"
    )

    filter = {"_id": convert_to_object_id(enquiry_id)}
    response = renting_enquiry_collection.find_one(filter=filter)

    if not response:
        return None

    enquiry = HorseRentingServiceEnquiryInternalWithID(**response)

    log.info(f"get_renting_enquiry_details_by_enquiry_id() returning enquiry {enquiry}")

    return enquiry


def get_renting_enquiry_by_user_id(
    user_id: str,
) -> List[HorseRentingServiceEnquiryInternalWithID]:
    """return all the horse rent enquiry made by the user

    Args:
        user_id (str): _description_

    Returns:
        List[HorseRentingServiceEnquiryInternalWithID]
    """

    log.info(f"get_renting_enquiry_by_user_id() called user_id {user_id}")

    filter = {"user_id": user_id}
    response = renting_enquiry_collection.find(filter=filter)

    if not response:
        return []

    enquiries = [
        HorseRentingServiceEnquiryInternalWithID(**enquiry) for enquiry in response
    ]

    log.info(f"get_renting_enquiry_by_user_id() returning {enquiries}")

    return enquiries


def get_all_horse_rent_enquiries() -> List[HorseRentingServiceEnquiryInternalWithID]:
    """return all the horse rent enquiry
    Returns:
        List[HorseRentingServiceEnquiryInternalWithID]
    """

    log.info(f"get_all_horse_rent_enquiries()")

    response = renting_enquiry_collection.find()

    if not response:
        return []

    enquiries = [
        HorseRentingServiceEnquiryInternalWithID(**enquiry) for enquiry in response
    ]

    log.info(f"get_all_horse_rent_enquiries() returning {enquiries}")

    return enquiries
