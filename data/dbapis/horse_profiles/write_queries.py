from data.db import get_horse_profiles_collection
from logging_config import log
from models.horse_profiles import HorseProfileInternal

horse_profiles_collection = get_horse_profiles_collection()


def save_horse_profile_db(horse_profile: HorseProfileInternal) -> str:
    """saves horse profile to the database

    Args:
        horse_profile (HorseProfileInternal)

    Returns:
        str: id
    """

    log.info(f"save_horse_profile_db invoked : {horse_profile}")
    horse_profile_id = (
        horse_profiles_collection.insert_one(horse_profile.model_dump())
    ).inserted_id

    retval = str(horse_profile_id)

    log.info(f"returning {retval}")

    return retval
