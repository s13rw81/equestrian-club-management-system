from typing import List, Union

from api.horses.models import GetHorseSellListing
from data.db import (
    convert_to_object_id,
    get_horse_selling_enquiry_collection,
    get_horse_selling_service_collection,
)
from logging_config import log
from models.horse.horse_selling_service_internal import (
    HorseSellingServiceEnquiryInternalWithID,
    HorseSellingServiceInternalWithID,
)

selling_service_collection = get_horse_selling_service_collection()
selling_enquiry_collection = get_horse_selling_enquiry_collection()


def get_selling_service_details_by_service_id(
    service_id: str,
) -> HorseSellingServiceInternalWithID:
    """based on service_id of horse selling service return the horse selling service details

    Args:
        service_id (str)

    Returns:
        HorseSellingServiceInternalWithID
    """

    log.info(
        f"get_selling_service_details_by_service_id() invoked service_id {service_id}"
    )

    filter = {"_id": convert_to_object_id(service_id)}
    response = selling_service_collection.find_one(filter=filter)

    selling_service_details = HorseSellingServiceInternalWithID(**response)

    log.info(
        f"get_selling_service_details_by_service_id() returning {selling_service_details}"
    )

    return selling_service_details


def get_horse_sell_listings(
    user_id: str, own_listing: bool = False
) -> List[GetHorseSellListing]:
    """return horses sell listings

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
            "horse_selling_service_id": "$_id",
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

    log.info(f"pipeline {pipeline}")

    response = selling_service_collection.aggregate(pipeline=pipeline)

    sell_listings = [GetHorseSellListing(**sell_listing) for sell_listing in response]

    return sell_listings


def get_selling_enquiry_details_by_user_and_selling_service_id(
    user_id: str, selling_service_id: str
) -> Union[HorseSellingServiceEnquiryInternalWithID, None]:
    """return an enquiry if the enquiry exists based on user_id and selling_service_id

    Args:
        user_id (str)
        selling_service_id (str)

    Returns:
        HorseSellingServiceEnquiryInternalWithID
    """

    log.info(
        f"get_selling_enquiry_details_by_user_and_selling_service_id() invoked user_id {user_id}, selling_service_id {selling_service_id}"
    )

    filter = {"user_id": user_id, "horse_selling_service_id": selling_service_id}

    response = selling_enquiry_collection.find_one(filter=filter)
    if not response:
        return None

    enquiry = HorseSellingServiceEnquiryInternalWithID(**response)

    log.info(
        f"get_selling_enquiry_details_by_user_and_selling_service_id() returning enquiry {enquiry}"
    )

    return enquiry


def get_selling_enquiry_details_by_enquiry_id(
    enquiry_id: str,
) -> Union[HorseSellingServiceEnquiryInternalWithID, None]:
    """return an enquiry if the enquiry exists based on the enquiry id

    Args:
        enquiry_id (str): _description_

    Returns:
        Union[HorseSellingServiceEnquiryInternalWithID, None]
    """

    log.info(
        f"get_selling_enquiry_details_by_enquiry_id() invoked enquiry_id {enquiry_id}"
    )

    filter = {"_id": convert_to_object_id(enquiry_id)}
    response = selling_enquiry_collection.find_one(filter=filter)

    if not response:
        return None

    enquiry = HorseSellingServiceEnquiryInternalWithID(**response)

    log.info(f"get_selling_enquiry_details_by_enquiry_id() returning enquiry {enquiry}")

    return enquiry


def get_selling_enquiry_by_user_id(
    user_id: str,
) -> List[HorseSellingServiceEnquiryInternalWithID]:
    """return all the horse sell enquiry made by the user

    Args:
        user_id (str): _description_

    Returns:
        List[HorseSellingServiceEnquiryInternalWithID]
    """

    log.info(f"get_selling_enquiry_by_user_id() called user_id {user_id}")

    filter = {"user_id": user_id}
    response = selling_enquiry_collection.find(filter=filter)

    if not response:
        return []

    enquiries = [
        HorseSellingServiceEnquiryInternalWithID(**enquiry) for enquiry in response
    ]

    log.info(f"get_selling_enquiry_by_user_id() returning {enquiries}")

    return enquiries


def get_all_horse_sell_enquiries() -> List[HorseSellingServiceEnquiryInternalWithID]:
    """return all the horse sell enquiry
    Returns:
        List[HorseSellingServiceEnquiryInternalWithID]
    """

    log.info(f"get_all_horse_sell_enquiries()")

    response = selling_enquiry_collection.find()

    if not response:
        return []

    enquiries = [
        HorseSellingServiceEnquiryInternalWithID(**enquiry) for enquiry in response
    ]

    log.info(f"get_all_horse_sell_enquiries() returning {enquiries}")

    return enquiries
