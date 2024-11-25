from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from data.dbapis.clubs import find_club, find_club_by_user, find_many_clubs
from data.dbapis.clubs import update_club as update_club_db
from data.dbapis.trainer_affiliation import save_trainer_affiliation
from logging_config import log
from logic.auth import get_current_user
from logic.clubs import (
    add_club_service,
    club_service_detailed_get_query_with_pagination,
    update_club_service,
    upload_images_logic,
    upload_logo_logic,
)
from logic.trainer_affiliation import trainer_affiliation_get_query_with_pagination
from models.clubs import UpdateClubInternal
from models.clubs.service_internal import ClubServiceInternal, UpdateClubServiceInternal
from models.http_responses import Success
from models.trainer_affiliation import TrainerAffiliationInternal
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl
from utils.image_management import generate_image_url, generate_image_urls

from ..commons.models import GetQueryPaginatedDTO
from .models import (
    GetClubDetailedDTO,
    GetClubDTO,
    GetTrainerAffiliationDetailedDTO,
    GetTrainerAffiliationDTO,
)
from .models.club_service import ResponseGetClubService
from .role_based_parameter_control import (
    ClubIdParameterControlForm,
    ClubServiceParameterControl,
    GenerateTrainerAffiliationParamControl,
    GetClubServicePaginatedParamControl,
    GetTrainerAffiliationPaginatedParamCtrl,
    UpdateClubParameterControl,
    UpdateClubServiceParameterControl,
)

clubs_api_router = APIRouter(prefix="/clubs", tags=["clubs"])


@clubs_api_router.put("/update-club")
async def update_club(
    request: Request,
    update_club_parameter_control: Annotated[UpdateClubParameterControl, Depends()],
):
    update_club_request = update_club_parameter_control.update_club_request
    user = update_club_parameter_control.user

    log.info(
        f"inside /clubs/update-club ("
        f"update_club_request={update_club_request}, "
        f"user={user})"
    )

    existing_club = find_club(id=str(update_club_request.id))

    update_club_data = UpdateClubInternal(
        last_updated_by=user.id,
        last_updated_on=datetime.now(pytz.utc),
        **update_club_request.model_dump(exclude_unset=True),
    )

    if update_club_request.club_id:
        log.info("club_id is provided in the update_data, creating new platform_id")
        platform_id_elements = existing_club.platform_id.split("_")
        new_platform_id = f"{platform_id_elements[0]}_{update_club_request.club_id}_{platform_id_elements[2]}"
        log.info(f"new platform_id={new_platform_id}")
        update_club_data.platform_id = new_platform_id

    updated_club = update_club_db(update_club_data=update_club_data)

    log.info("club updated successfully, returning...")

    return Success(
        message="club updated successfully...",
        data={
            "updated_club": GetClubDTO(
                logo=generate_image_url(image_id=updated_club.logo, request=request),
                images=generate_image_urls(
                    image_ids=updated_club.images, request=request
                ),
                **updated_club.model_dump(exclude={"logo", "images"}),
            )
        },
    )


@clubs_api_router.get("/get-club/{club_id}")
async def get_club_by_id(
    request: Request,
    club_id: str,
    user: Annotated[UserInternal, Depends(get_current_user)],
):
    log.info(f"inside /clubs/get-club/{club_id} (club_id={club_id}, user_id={user.id})")

    club = find_club(id=club_id)

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no club exists with the provided id (club_id={club_id})",
        )

    retval = Success(
        message="club retrieved successfully...",
        data=GetClubDetailedDTO(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"}),
        ),
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-clubs")
async def get_clubs(
    request: Request, user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /clubs/get-clubs (user_id={user.id})")

    clubs = find_many_clubs()

    retval = Success(
        message="club retrieved successfully...",
        data=[
            GetClubDTO(
                logo=generate_image_url(image_id=club.logo, request=request),
                images=generate_image_urls(image_ids=club.images, request=request),
                **club.model_dump(exclude={"logo", "images"}),
            )
            for club in clubs
        ],
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-your-club")
async def get_your_club(
    request: Request,
    user: Annotated[
        UserInternal, Depends(RoleBasedAccessControl(allowed_roles={UserRoles.CLUB}))
    ],
):
    log.info(f"inside /clubs/get-your-club (user_id={user.id})")

    club = find_club_by_user(user_id=str(user.id))

    retval = Success(
        message="club retrieved successfully...",
        data=GetClubDTO(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"}),
        ),
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-logo")
async def upload_logo(
    request: Request,
    logo: UploadFile,
    club_id_parameter_control: Annotated[ClubIdParameterControlForm, Depends()],
):
    user = club_id_parameter_control.user
    club_id = club_id_parameter_control.club_id

    log.info(f"inside /clubs/upload-logo(user_id={user.id}, club_id={club_id})")

    club = await upload_logo_logic(club_id=club_id, logo=logo)

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClubDTO(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"}),
        ),
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-images")
async def upload_logo(
    request: Request,
    images: list[UploadFile],
    club_id_parameter_control: Annotated[ClubIdParameterControlForm, Depends()],
):
    user = club_id_parameter_control.user
    club_id = club_id_parameter_control.club_id

    log.info(f"inside /clubs/upload-images(user_id={user.id}, club_id={club_id})")

    club = await upload_images_logic(club_id=club_id, images=images)

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClubDTO(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"}),
        ),
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/generate-trainer-affiliation")
async def generate_trainer_affiliation(
    generate_trainer_affiliation_param_control: Annotated[
        GenerateTrainerAffiliationParamControl, Depends()
    ]
):
    user = generate_trainer_affiliation_param_control.user
    generate_trainer_affiliation_dto = (
        generate_trainer_affiliation_param_control.generate_trainer_affiliation_dto
    )

    log.info(
        f"inside /clubs/generate-trainer-affiliation (user={user}, "
        f"generate_trainer_affiliation_dto={generate_trainer_affiliation_dto})"
    )

    new_trainer_affiliation = TrainerAffiliationInternal(
        created_by=user.id, **generate_trainer_affiliation_dto.model_dump()
    )

    trainer_affiliation = save_trainer_affiliation(
        new_trainer_affiliation=new_trainer_affiliation
    )

    retval = Success(
        message="trainer affiliation number generated successfully",
        data=GetTrainerAffiliationDTO(**trainer_affiliation.model_dump()),
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-trainer-affiliation-paginated")
async def get_trainer_affiliation_paginated(
    get_trainer_affiliation_param_ctrl: Annotated[
        GetTrainerAffiliationPaginatedParamCtrl, Depends()
    ]
):
    user = get_trainer_affiliation_param_ctrl.user
    get_query_paginated_dto = get_trainer_affiliation_param_ctrl.get_query_paginated_dto

    f = get_query_paginated_dto.f
    s = get_query_paginated_dto.s
    page_no = get_query_paginated_dto.page_no
    page_size = get_query_paginated_dto.page_size

    log.info(
        f"inside /clubs/get-trainer-affiliation-paginated ("
        f"f={f}, s={s}, page_no={page_no}, page_size={page_size}, user_id={user.id})"
    )

    result = trainer_affiliation_get_query_with_pagination(
        f=f, s=s, page_no=page_no, page_size=page_size
    )

    log.info(f"received data = {result}")

    retval = Success(
        message="trainer affiliation details fetched successfully",
        data=[GetTrainerAffiliationDetailedDTO(**data.model_dump()) for data in result],
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/{club_id}/services")
def add_a_new_club_service(
    request: Request,
    club_service_parameter_control: Annotated[ClubServiceParameterControl, Depends()],
):
    user = club_service_parameter_control.user
    club_id = club_service_parameter_control.club_id
    club_service = club_service_parameter_control.club_service

    log.info(
        f"inside {request.url} invoked (create_club_service_request={club_service}, user_id={user.id})"
    )

    club_service_internal = ClubServiceInternal(
        created_by=user.id,
        club_id=club_id,
        **club_service.model_dump(exclude={"availability"}),
    )
    service_availability = club_service.availability

    newly_created_club_service = add_club_service(
        club_service=club_service_internal,
        user=user,
        service_availability=service_availability,
    )

    return Success(
        message="club service added successfully",
        data={"id": newly_created_club_service.id},
    )


@clubs_api_router.put("/{club_id}/services/{club_service_id}")
def update_a_club_service(
    request: Request,
    update_club_service_parameter_control: Annotated[
        UpdateClubServiceParameterControl, Depends()
    ],
):
    user = update_club_service_parameter_control.user
    club_id = update_club_service_parameter_control.club_id
    club_service_id = update_club_service_parameter_control.club_service_id
    club_service = update_club_service_parameter_control.club_service

    log.info(
        f"{request.url} invoked user={user}, club_id={club_id}, club_service_id={club_service_id}, club_service={club_service}"
    )

    update_club_service_internal = UpdateClubServiceInternal(
        last_updated_by=user.id,
        club_id=club_id,
        id=club_service_id,
        **club_service.model_dump(exclude_unset=True),
    )
    service_availability = club_service.availability

    updated_club_service = update_club_service(
        club_service=update_club_service_internal,
        club_service_id=club_service_id,
        user=user,
        service_availability=service_availability,
    )

    return Success(
        message="club service updated successfully", data={"id": club_service_id}
    )


@clubs_api_router.get("/{club_id}/services/")
def get_club_service_detailed_with_pagination(
    request: Request,
    get_club_services_param_control: Annotated[
        GetClubServicePaginatedParamControl, Depends()
    ],
):
    user = get_club_services_param_control.user
    club_id = get_club_services_param_control.club_id
    get_query_paginated_dto = get_club_services_param_control.get_query_paginated_dto

    f = get_query_paginated_dto.f
    s = get_query_paginated_dto.s
    page_no = get_query_paginated_dto.page_no
    page_size = get_query_paginated_dto.page_size

    log.info(
        f"{request.url} invoked user={user}, club_id={club_id},"
        f"f={f}, s={s}, page_no={page_no}, page_size={page_size}"
    )

    result = club_service_detailed_get_query_with_pagination(
        f=f, s=s, page_no=page_no, page_size=page_size
    )

    log.info(f"received data = {result}")

    retval = Success(
        message="club service details fetched successfully",
        data=[ResponseGetClubService(**data.model_dump()) for data in result],
    )

    log.info(f"returning {retval}")

    return retval
