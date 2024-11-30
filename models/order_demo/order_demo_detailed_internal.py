from . import OrderDemoInternal
from ..generic_get_query_with_pagination import Lookup
from ..user import UserInternal
from ..clubs import ClubInternal
from typing import Annotated

class OrderDemoDetailedInternal(OrderDemoInternal):
    user: Annotated[
        UserInternal,
        Lookup(
            from_collection="users",
            local_field="user_id",
            foreign_field="id",
            as_key_name="user",
            is_one_to_one=True
        )
    ]
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
