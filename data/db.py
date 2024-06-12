from typing import Annotated

from bson.objectid import ObjectId
from pydantic import BeforeValidator
from pymongo import MongoClient

from config import DATABASE_MAX_POOL_SIZE, DATABASE_NAME
from logging_config import log

CONNECTION_STRING = "mongodb://localhost:27017"
PyObjectId = Annotated[str, BeforeValidator(str)]


def get_database():
    log.info("inside get_database()")
    client = MongoClient(CONNECTION_STRING, maxPoolSize=DATABASE_MAX_POOL_SIZE)
    log.info("returning from get_database()")
    return client[DATABASE_NAME]


def get_users_collection():
    # TODO: create a unique index in the email_address field
    log.info("inside get_users_collection()")
    return get_database()["users"]


def get_transfer_collection():
    log.info("inside get_transfer_collection()")
    return get_database()["transfers"]


def convert_to_object_id(str_id: str) -> ObjectId:
    """
    converts the provided id in string into bson.ObjectId (
    compatible with mongo database)

    :param str_id: str
    :returns: ObjectId
    """
    return ObjectId(str_id)
