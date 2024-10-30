from data.db import get_countries_collection
from logging_config import log
from models.user.country_internal import CountryInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction

country_collection = get_countries_collection()


@atomic_transaction
def save_country(country: CountryInternal, session=None) -> CountryInternal:
    log.info(f"save_country invoked: {country}")

    try:
        # Insert the document into the collection
        result = country_collection.insert_one(country.model_dump(), session=session)

        if not result.acknowledged:
            log.info("New country can't be inserted in the database, raising exception...")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="New country can't be inserted in the database due to unknown reasons."
            )

        log.info(f"New country has successfully been inserted (country_id={country.id})")
    except Exception as e:
        log.error(f"Error inserting country: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to insert the country into the database"
        )

    return country
