from typing import Annotated
from urllib.parse import quote_plus
from bson.objectid import ObjectId
from pydantic import BeforeValidator
from pymongo import MongoClient
from config import (
    DATABASE_MAX_POOL_SIZE,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_URL,
    DATABASE_USER,
    DATABASE_REPLICA_SET_NAME
)
from logging_config import log

ESCAPED_DATABASE_USERNAME = quote_plus(DATABASE_USER)
ESCAPED_DATABASE_PASSWORD = quote_plus(DATABASE_PASSWORD)

CONNECTION_STRING = (
    f"mongodb://{ESCAPED_DATABASE_USERNAME}:{ESCAPED_DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}"
    if ESCAPED_DATABASE_USERNAME != ""
    else f"mongodb://{DATABASE_URL}:{DATABASE_PORT}"
)

CONNECTION_STRING += f"/?replicaSet={DATABASE_REPLICA_SET_NAME}&directConnection=true"

client = MongoClient(CONNECTION_STRING, maxPoolSize=DATABASE_MAX_POOL_SIZE)

PyObjectId = Annotated[str, BeforeValidator(str)]




def get_database():
    log.info("inside get_database()")
    return client[DATABASE_NAME]


def get_users_collection():
    # TODO: create a unique index in the email_address field
    log.info("inside get_users_collection()")
    return get_database()["users"]


def get_collection(collection_name: str):
    log.info(f"inside get_collection : {collection_name}")
    return get_database()[collection_name]


def get_transfer_collection():
    log.info("inside get_transfer_collection()")
    return get_database()["transfers"]


def get_customer_transfer_collection():
    log.info("inside get_customer_transfer_collection()")
    return get_database()["customer_transfers"]


def get_horse_profiles_collection():
    log.info(f"inside get_horse_profile_collection()")
    return get_database()["horse_profiles"]


def get_groomers_info_collection():
    log.info(f"inside get_groomers_info_collection()")
    return get_database()["groomers"]


def get_truck_collection():
    log.info("inside get_truck_collection()")
    return get_database()["trucks"]


def get_company_collection():
    log.info("inside get_company_collection()")
    return get_database()["company"]


def get_clubs_collection():
    log.info("inside get_club_collection()")
    club_collection = get_database()["club"]
    club_collection.create_index([("id", 1)], unique=True)
    return club_collection


def get_horses_collection():
    log.info("inside get_horses_collection")
    return get_database()["horses_collection"]


def get_logistics_company_collection():
    log.info("inside get_clubs_collection()")
    return get_database()["logistic_company"]


def get_riding_lesson_bookings_collection():
    log.info("inside get_clubs_collection()")
    return get_database()["riding_lesson_service_booking"]


def get_horse_shoeing_service_bookings_collection():
    log.info("inside get_clubs_collection()")
    return get_database()["horse_shoeing_service_bookings"]


def get_riding_lesson_collection():
    log.info("inside get_riding_lesson_collection()")
    return get_database()["riding_lesson_service"]


def get_horse_shoeing_service_collection():
    log.info("inside get_horse_shoeing_service_collection()")
    return get_database()["horse_shoeing_service"]


def get_horses_selling_collection():
    log.info("inside get_horses_selling_collection")
    return get_database()["horses_selling_collection"]


def get_horses_selling_service_collection():
    log.info("inside get_horses_selling_service_collection")
    return get_database()["horses_selling_service_collection"]


def get_horses_renting_service_collection():
    log.info("inside get_horses_renting_service_collection")
    return get_database()["horses_renting_service_collection"]


def get_horses_renting_collection():
    log.info("inside get_horses_selling_collection")
    return get_database()["horses_selling_collection"]


def get_uploaded_images_collection():
    log.info("inside get_uploaded_images_collection")
    return get_database()["uploaded_images_collection"]


def get_upload_images_demo_collection():
    log.info("inside get_upload_images_demo()")
    return get_database()["upload_images_demo"]


def get_horse_collection():
    log.info("inside get_horse_collection()")
    return get_database()["horses"]


def get_horse_selling_service_collection():
    log.info("inside get_horse_renting_service_collection()")
    return get_database()["horse_selling_service"]


def get_horse_selling_enquiry_collection():
    log.info("inside get_horse_renting_enquiry_collection()")
    return get_database()["horse_selling_enquiry"]


def get_horse_renting_service_collection():
    log.info("inside get_horse_renting_service_collection()")
    return get_database()["horse_renting_service"]


def get_horse_renting_enquiry_collection():
    log.info("inside get_horse_renting_enquiry_collection()")
    return get_database()["horse_renting_enquiry"]


def get_trainer_collection():
    log.info("inside get_trainer_collection")
    return get_database()["trainer"]


def get_generic_activity_service_collection():
    log.info("inside get_generic_activity_service_collection")
    return get_database()["generic_activity_service"]


def get_generic_activity_service_bookings_collection():
    log.info("inside get_generic_activity_service_collection")
    return get_database()["generic_activity_service_booking"]


def get_reviews_collection():
    log.info("inside get_reviews_collection")
    return get_database()["reviews"]


def get_logistic_service_booking_collection():
    log.info("inside get_logistic_service_booking_collection()")
    return get_database()["logistic_service_booking"]


def convert_to_object_id(str_id: str) -> ObjectId:
    """
    converts the provided id in string into bson.ObjectId (
    compatible with mongo database)

    :param str_id: str
    :returns: ObjectId
    """
    return ObjectId(str_id)
