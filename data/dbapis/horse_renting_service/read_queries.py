from typing import List, Union

from api.horses.models import GetHorseRentListing
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


def get_horse_rent_listings(
    user_id: str, own_listing: bool = False
) -> List[GetHorseRentListing]:
    """return horses rent listings

    Args:
        own_listing (bool, optional):  Defaults to False.
    """

    match = {
        "$match": (
            {"provider.provider_id": user_id}
            if own_listing
            else {"provider.provider_id": {"$ne": user_id}}
        )
    }

    add_fields_provider = {
        "$addFields": {
            "provider_object_id": {"$toObjectId": "$provider.provider_id"},
        }
    }

    add_fields_horses = {
        "$addFields": {"horse_object_id": {"$toObjectId": "$horse_id"}}
    }

    lookup_users = {
        "$lookup": {
            "from": "users",
            "localField": "provider_object_id",
            "foreignField": "_id",
            "as": "user",
        }
    }

    unwind_users = {"$unwind": "$user"}

    lookup_horses = {
        "$lookup": {
            "from": "horses",
            "localField": "horse_object_id",
            "foreignField": "_id",
            "as": "horse",
        }
    }

    unwind_horses = {"$unwind": "$horse"}

    project = {
        "$project": {
            "horse_renting_service_id": "$_id",
            "horse_id": "$horse_id",
            "name": "$horse.name",
            "year_of_birth": "$horse.year_of_birth",
            "breed": "$horse.breed",
            "size": "$horse.size",
            "gender": "$horse.gender",
            "description": "$horse.description",
            "image_urls": "$images",
            "price": "$price_sar",
            "seller_information": {
                "name": "$user.full_name",
                "email_address": "$user.email_address",
                "phone_no": "$user.phone_number",
                "location": "$user.address",
            },
            "_id": False,
        }
    }

    pipeline = [
        match,
        add_fields_provider,
        add_fields_horses,
        lookup_users,
        unwind_users,
        lookup_horses,
        unwind_horses,
        project,
    ]

    response = renting_service_collection.aggregate(pipeline=pipeline)

    rent_listings = [GetHorseRentListing(**rent_listing) for rent_listing in response]

    return rent_listings


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
