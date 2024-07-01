from collections import namedtuple
from typing import Tuple

from data.dbapis.truck.read_queries import (
    get_truck_details_by_id_db,
    get_trucks_by_service_id,
)
from logging_config import log
from models.truck.enums import TruckAvailability
from utils.logistics_utils import LogisticsService

truck_availability_response = namedtuple(
    "TruckAvailabilityForServiceBooking", ["is_available", "message"]
)


def truck_available_for_service_booking(
    service_id: str,
    service_type: str,
    logistics_company_id: str,
    truck_id: str,
) -> truck_availability_response:
    """checks if the truck works for the provided service.
    check is the status of the truck is available.
    checks if the truck belongs to the provided logistics_company_id

    Args:
        service_id (str)
        service_type (str)
        logistics_company_id (str)
        truck_id (str)

    Returns:
        truck_availability_response: is_available, message
    """
    truck_available_for_service = get_trucks_by_service_id(
        service_id=service_id,
        service_type=service_type,
    )
    if truck_id not in truck_available_for_service:
        return truck_availability_response(
            is_available=False,
            message="provided truck is not available for this service",
        )

    truck_details = get_truck_details_by_id_db(
        truck_id=truck_id,
        fields=["logistics_company_id", "availability"],
    )

    if truck_details.get("logistics_company_id") != logistics_company_id:
        return truck_availability_response(
            is_available=False, message="invalid logistics company selected"
        )

    truck_available = (
        truck_details.get("availability") == TruckAvailability.AVAILABLE.value
    )
    if not truck_available:
        return truck_availability_response(
            is_available=False, message="selected truck is not currently available"
        )

    return truck_availability_response(is_available=True, message=None)
