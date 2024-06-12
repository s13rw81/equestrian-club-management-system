from pymongo import MongoClient
from bson.objectid import ObjectId
from config import DATABASE_NAME, DATABASE_MAX_POOL_SIZE, DATABASE_URL, DATABASE_PASSWORD, DATABASE_USER, DATABASE_PORT
from logging_config import log
from urllib.parse import quote_plus

ESCAPED_DATABASE_USERNAME = quote_plus(DATABASE_USER)
ESCAPED_DATABASE_PASSWORD = quote_plus(DATABASE_PASSWORD)

CONNECTION_STRING = (f"mongodb://{ESCAPED_DATABASE_USERNAME}:{ESCAPED_DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}"
                     if ESCAPED_DATABASE_USERNAME != "" else f"mongodb://{DATABASE_URL}:{DATABASE_PORT}")


def get_database():
    log.info("inside get_database()")
    client = MongoClient(CONNECTION_STRING, maxPoolSize=DATABASE_MAX_POOL_SIZE)
    log.info("returning from get_database()")
    return client[DATABASE_NAME]


def get_users_collection():
    # TODO: create a unique index in the email_address field
    log.info("inside get_users_collection()")
    return get_database()['users']


def convert_to_object_id(str_id: str) -> ObjectId:
    """
    converts the provided id in string into bson.ObjectId (
    compatible with mongo database)

    :param str_id: str
    :returns: ObjectId
    """
    return ObjectId(str_id)
