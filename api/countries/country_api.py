from uuid import UUID
from fastapi import APIRouter, status, Request, Depends
from fastapi.exceptions import HTTPException
from api.countries.models.country_model import CreateCountryDTO
from data.dbapis.country.read_queries import fetch_country_by_uuid, list_country
from data.dbapis.country.write_queries import save_country
from logging_config import log
from logic.auth import get_current_user
from models.http_responses import Success
from models.user import UserInternal
from models.user.country_internal import CountryInternal
from typing import Annotated

country_api_router = APIRouter(
    prefix="/country",
    tags=["country"]
)

"""__________________________________________________________________________________________________________________"""


# Create country API
@country_api_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_country(request: Request, country: CreateCountryDTO,
                         user: Annotated[UserInternal, Depends(get_current_user)]):
    log.info(f"/create invoked by user {user.id}: country = {country}")

    # Convert to internal country model for database, associating it with the user
    country = CountryInternal(
        country_name=country.country_name,
        country_code=country.country_code,
        country_iso=country.country_iso,
        created_by=user.id  # Assuming CountryInternal has a created_by field
    )

    # Save the country
    result = save_country(country=country)

    if not result:
        log.error(f"User {user.id} could not save the country in the database, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the country in the database"
        )

    # Create response with success message and saved country data
    retval = Success(
        message="Country created successfully",
        data={
            "country_name": country.country_name,
            "country_code": country.country_code,
            "country_iso": country.country_iso,
            "created_by": user.id  # Optionally return the creator's ID in the response
        }
    )

    log.info(f"Returning {retval} for user {user.id}")
    return retval


@country_api_router.get("/all")
async def get_all_countries():
    log.info("/countries invoked")

    # Use list_country function to fetch all countries
    countries = list_country()  # Fetch the countries

    if not countries:
        log.info("No countries found in the database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No countries found"
        )

    log.info(f"Countries retrieved: {countries}")

    return Success(
        message="Countries fetched successfully.",
        data=[country.model_dump() for country in countries]  # Used model_dump to convert Pydantic models to dict(as
        # recommended)
    )


# Fetch country by UUID API
@country_api_router.get("/{country_uuid}")
async def get_country_by_uuid(country_uuid: UUID):
    log.info(f"/country/{country_uuid} invoked")

    # Use get_country_by_uuid function to fetch country by UUID
    country = fetch_country_by_uuid(country_id=country_uuid)

    if not country:
        log.error(f"Country with UUID {country_uuid} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    log.info(f"Country retrieved: {country}")

    return Success(
        message="Country fetched successfully.",
        data=country
    )


"""__________________________________________________________________________________________________________________"""
