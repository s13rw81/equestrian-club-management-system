from uuid import UUID

from models.user.country_internal import CountryInternal
from data.db import get_countries_collection
from logging_config import log
from decorators import atomic_transaction
from typing import Optional

country_collection = get_countries_collection()


@atomic_transaction
def list_country(session=None) -> Optional[list[CountryInternal]]:
    log.info("Fetching all countries")

    countries = list(country_collection.find({}, session=session))  # Fetch all countries
    if not countries:
        log.info("No countries found in the database.")
        return []

    # Convert ObjectId and create a list of CountryInternal objects
    for country in countries:
        country['_id'] = str(country['_id'])  # Convert ObjectId to string

    return [CountryInternal(**country) for country in countries]  # Return a list of CountryInternal objects


def fetch_country_by_uuid(country_id: UUID) -> CountryInternal | None:
    log.info(f"get_country_by_uuid invoked: country_id={country_id}")

    country = country_collection.find_one({"id": str(country_id)})

    if country is None:
        retval = None
    else:
        retval = CountryInternal(**country)

    log.info(f"returning {retval}")

    return retval
