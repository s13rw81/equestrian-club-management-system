from typing import Annotated

from models.generic_get_query_with_pagination import Lookup

from .service_internal import AvailabilityInternal, ClubServiceInternal


class ClubServiceDetailedInternal(ClubServiceInternal):
    availability: Annotated[
        list[AvailabilityInternal],
        Lookup(
            from_collection="club_service_availability",
            local_field="id",
            foreign_field="club_service_id",
            as_key_name="availability",
            is_one_to_one=False,
        ),
    ] = []
