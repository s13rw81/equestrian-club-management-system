from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from data.dbapis.logistics_company_services.read_queries import (
    club_to_club_service_by_logistics_company_id,
    get_club_to_club_service_by_service_id,
    get_logistics_company_by_id,
    get_luggage_transfer_service_by_logistics_company_id,
    get_luggage_transfer_service_by_service_id,
    get_user_transfer_service_by_logistics_company_id,
    get_user_transfer_service_by_service_id,
)
from data.dbapis.logistics_company_services.write_queries import (
    save_club_to_club_service_db,
    save_luggage_transfer_service_db,
    save_user_transfer_service_db,
    update_club_to_club_service,
    update_luggage_transfer_service_db,
    update_user_transfer_service_db,
)
from logging_config import log
from models.logistics_company_services import (
    ClubToClubServiceInternal,
    LuggageTransferServiceInternal,
    Provider,
    UserTransferServiceInternal,
)
from models.logistics_company_services.enums.service_enums import ServiceAvailability
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl

from .api_validators.logistics_company_services import (
    AddClubToClubServiceValidator,
    GetClubToClubServiceValidator,
)
from .models import (
    AddClubToClubService,
    AddLuggageTransferService,
    AddUserTransferService,
    ResponseAddClubToClubService,
    ResponseAddLuggageTransferService,
    ResponseAddUserTransferService,
    ResponseGetClubToClubService,
    ResponseGetLuggageTransferService,
    ResponseGetUserTransferService,
    UpdateClubToClubService,
    UpdateLuggageTransferService,
    UpdateUserTransferService,
)

manage_service_router = APIRouter(prefix="/services", tags=["logistics-company"])


@manage_service_router.get("/get-club-to-club-service")
def get_club_to_club_transfer_service(
    request: Request, payload: Annotated[GetClubToClubServiceValidator, Depends()]
) -> ResponseGetClubToClubService:

    logistics_company_id = payload.logistics_company_id

    log.info(f"{request.url.path} invoked")

    service_details = club_to_club_service_by_logistics_company_id(
        logistics_company_id=logistics_company_id
    )
    if not service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the logistic company does not provide this service",
        )

    response = ResponseGetClubToClubService(
        service_id=service_details.service_id,
        logistics_company_id=service_details.provider.provider_id,
        trucks=service_details.trucks,
        created_at=service_details.created_at,
        updated_at=service_details.updated_at,
        is_available=service_details.is_available,
        features=service_details.features,
        description=service_details.description,
        images=service_details.images,
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.post("/add-club-to-club-service")
def add_club_to_club_transfer_service(
    request: Request, payload: Annotated[AddClubToClubServiceValidator, Depends()]
) -> ResponseAddClubToClubService:

    club_to_club_service_details = payload.service_details
    logistics_company_id = payload.logistics_company_id

    log.info(f"{request.url.path} invoked : {club_to_club_service_details}")

    provider = Provider(
        provider_id=logistics_company_id,
        provider_type=UserRoles.LOGISTIC_COMPANY,
    )
    club_to_club_service = ClubToClubServiceInternal(
        provider=provider,
        is_available=ServiceAvailability.AVAILABLE,
        trucks=club_to_club_service_details.trucks,
        features=club_to_club_service_details.features,
        description=club_to_club_service_details.description,
    )

    service_id = save_club_to_club_service_db(service=club_to_club_service)
    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save service",
        )

    response = ResponseAddClubToClubService(logistic_service_club_to_club_id=service_id)

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.put("/update-club-to-club-service/{service_id}")
def update_club_to_club_transfer_service(
    service_id: str,
    service_update_details: UpdateClubToClubService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked : {service_update_details}")

    service_details = get_club_to_club_service_by_service_id(service_id=service_id)

    if service_details.is_available.value == service_update_details.is_available.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid availability status provided",
        )

    service_updated = update_club_to_club_service(
        service_id=service_id, update_details=service_update_details
    )

    if not service_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to update service",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@manage_service_router.get("/get-user-transfer-service/{logistics_company_id}")
def get_user_transfer_service(
    logistics_company_id: str,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
) -> ResponseGetUserTransferService:
    log.info(f"{request.url.path} invoked")

    service_details = get_user_transfer_service_by_logistics_company_id(
        logistics_company_id=logistics_company_id
    )
    if not service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the logistic company does not provide this service",
        )

    response = ResponseGetUserTransferService(
        service_id=service_details.service_id,
        logistics_company_id=service_details.provider.provider_id,
        trucks=service_details.trucks,
        created_at=service_details.created_at,
        updated_at=service_details.updated_at,
        is_available=service_details.is_available,
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.post("/add-user-transfer-service")
def add_user_transfer_service(
    user_service_details: AddUserTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
) -> ResponseAddUserTransferService:
    log.info(f"{request.url.path} invoked : {user_service_details}")

    logistics_company_details = get_logistics_company_by_id(
        logistics_company_id=user_service_details.logistics_company_id
    )
    if not logistics_company_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="logistics company does not exist.",
        )

    service_details = get_user_transfer_service_by_logistics_company_id(
        logistics_company_id=user_service_details.logistics_company_id
    )
    if service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user transfer service already exists for the logistics company",
        )

    provider = Provider(
        provider_id=user_service_details.logistics_company_id,
        provider_type=UserRoles.LOGISTIC_COMPANY,
    )
    user_transfer_service = UserTransferServiceInternal(
        provider=provider, is_available=ServiceAvailability.AVAILABLE
    )

    service_id = save_user_transfer_service_db(service=user_transfer_service)
    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save service",
        )

    response = ResponseAddUserTransferService(service_id=service_id)

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.put("/update-user-transfer-service")
def update_user_transfer_service(
    service_id: str,
    service_update_details: UpdateUserTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked : {service_update_details}")

    service_details = get_user_transfer_service_by_service_id(service_id=service_id)

    if service_details.is_available.value == service_update_details.is_available.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid availability status provided",
        )

    service_updated = update_user_transfer_service_db(
        service_id=service_id, update_details=service_update_details
    )

    if not service_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to update service",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@manage_service_router.get("/get-luggage-transfer-service/{logistics_company_id}")
def get_luggage_transfer_service(
    logistics_company_id: str,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
) -> ResponseGetLuggageTransferService:
    log.info(f"{request.url.path} invoked")

    service_details = get_luggage_transfer_service_by_logistics_company_id(
        logistics_company_id=logistics_company_id
    )
    if not service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the logistic company does not provide this service",
        )

    response = ResponseGetLuggageTransferService(
        service_id=service_details.service_id,
        logistics_company_id=service_details.provider.provider_id,
        trucks=service_details.trucks,
        created_at=service_details.created_at,
        updated_at=service_details.updated_at,
        is_available=service_details.is_available,
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.post("/add-luggage-transfer-service")
def add_luggage_transfer_service(
    luggage_transfer_service_details: AddLuggageTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
) -> ResponseAddLuggageTransferService:
    log.info(f"{request.url.path} invoked : {luggage_transfer_service_details}")

    logistics_company_details = get_logistics_company_by_id(
        logistics_company_id=luggage_transfer_service_details.logistics_company_id
    )
    if not logistics_company_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="logistics company does not exist.",
        )

    service_details = get_luggage_transfer_service_by_logistics_company_id(
        logistics_company_id=luggage_transfer_service_details.logistics_company_id
    )
    if service_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="luggage transfer service already exists for the logistics company",
        )

    provider = Provider(
        provider_id=luggage_transfer_service_details.logistics_company_id,
        provider_type=UserRoles.LOGISTIC_COMPANY,
    )
    luggage_transfer_service = LuggageTransferServiceInternal(
        provider=provider, is_available=ServiceAvailability.AVAILABLE
    )

    service_id = save_luggage_transfer_service_db(service=luggage_transfer_service)
    if not service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save service",
        )

    response = ResponseAddLuggageTransferService(service_id=service_id)

    log.info(f"{request.url.path} returning : {response}")

    return response


@manage_service_router.put("/update-luggage-transfer-service")
def update_luggage_transfer_service(
    service_id: str,
    service_update_details: UpdateLuggageTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={UserRoles.ADMIN, UserRoles.LOGISTIC_COMPANY}
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked : {service_update_details}")

    service_details = get_luggage_transfer_service_by_service_id(service_id=service_id)

    if service_details.is_available.value == service_update_details.is_available.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid availability status provided",
        )

    service_updated = update_luggage_transfer_service_db(
        service_id=service_id, update_details=service_update_details
    )

    if not service_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to update service",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
