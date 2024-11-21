from fastapi import Depends, Query
from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles
from models.user import UserInternal
from ...commons.models import GetQueryPaginatedDTO
from typing import Annotated
from data.dbapis.clubs import find_club_by_user
from data.dbapis.trainers import find_trainer

class GetTrainerAffiliationPaginatedParamCtrl:
    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(
                    RoleBasedAccessControl(
                        allowed_roles={UserRoles.ADMIN, UserRoles.CLUB, UserRoles.TRAINER, UserRoles.USER}
                    )
                )
            ],
            get_query_paginated_dto: Annotated[GetQueryPaginatedDTO, Query()]
    ):
        filter_predicates = get_query_paginated_dto.f if get_query_paginated_dto.f else []

        if user.user_role == UserRoles.CLUB:
            club = find_club_by_user(user_id=str(user.id))
            filter_predicates.append(f"club_id$eq${club.id}")

        elif user.user_role == UserRoles.TRAINER:
            trainer = find_trainer(user_id=str(user.id))
            filter_predicates.append(f"phone_number$eq${trainer.phone_number}")

        elif user.user_role == UserRoles.USER:
            filter_predicates.append(f"phone_number$eq${user.phone_number}")

        get_query_paginated_dto.f = filter_predicates

        self.user = user
        self.get_query_paginated_dto = get_query_paginated_dto