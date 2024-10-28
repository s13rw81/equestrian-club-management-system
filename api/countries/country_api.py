from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from data.db import get_countries_collection
from logging_config import log
from models.http_responses import Success


country_api_router = APIRouter(
    prefix="/country",
    tags=["country"]
)

"""__________________________________________________________________________________________________________________"""


# Fetch all countries API
@country_api_router.get("/all")
async def get_all_countries():
    log.info("/countries invoked")

    countries = get_countries_collection()

    if not countries:
        log.info("No countries found in the database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No countries found"
        )

    log.info(f"Countries retrieved: {countries}")

    return Success(
        message="Countries fetched successfully.",
        data=countries
    )


"""__________________________________________________________________________________________________________________"""
