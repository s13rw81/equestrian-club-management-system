from ..trainer_affiliation import TrainerAffiliationInternal
from ..generic_get_query_with_pagination import Lookup
from ..clubs import ClubInternal
from typing import Annotated


class TrainerAffiliationDetailedInternal(TrainerAffiliationInternal):
    club: Annotated[
        ClubInternal,
        Lookup(
            from_collection="clubs",
            local_field="club_id",
            foreign_field="id",
            as_key_name="club",
            is_one_to_one=True
        )
    ]