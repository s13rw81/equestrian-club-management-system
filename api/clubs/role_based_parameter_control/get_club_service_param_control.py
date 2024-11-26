from typing import Annotated, Optional

from fastapi import Depends, Query

from data.dbapis.clubs import find_club_by_user
from data.dbapis.trainers import find_trainer
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl

from ...commons.models import GetQueryPaginatedDTO


class GetClubServicePaginatedParamControl:
    def __init__(
        self,
        user: Annotated[
            UserInternal,
            Depends(
                RoleBasedAccessControl(
                    allowed_roles={
                        UserRoles.ADMIN,
                        UserRoles.CLUB,
                        UserRoles.TRAINER,
                        UserRoles.USER,
                    }
                )
            ),
        ],
        get_query_paginated_dto: Annotated[GetQueryPaginatedDTO, Query()],
        club_id: str,
    ):
        filter_predicates = (
            get_query_paginated_dto.f if get_query_paginated_dto.f else []
        )

        if user.user_role == UserRoles.CLUB:
            club = find_club_by_user(user_id=str(user.id))
            filter_predicates.append(f"club_id$eq${club.id}")

        elif user.user_role == UserRoles.TRAINER:
            trainer = find_trainer(user_id=str(user.id))
            filter_predicates.append(f"club_id$eq${trainer.club_id}")

        get_query_paginated_dto.f = filter_predicates

        self.user = user
        self.get_query_paginated_dto = get_query_paginated_dto
        self.club_id = club_id
