from fastapi import APIRouter, Depends, Request, HTTPException, status, UploadFile
from .role_based_parameter_control import (
    ClubIdParameterControlForm,
    ClubIdParameterControlBody,
    UpdateClubParameterControl
)
from typing import Annotated, Optional
from logging_config import log
from data.dbapis.clubs import find_club, update_club as update_club_db, find_club_by_user, find_many_clubs
from models.clubs import UpdateClubInternal
from models.user import UserInternal
from models.trainer_affiliation import TrainerAffiliationInternal
from logic.auth import get_current_user
from logic.clubs import upload_logo_logic, upload_images_logic
from models.http_responses import Success
from .models import (
    GetClub,
    GetClubDetailedDTO,
    GenerateTrainerAffiliationDTO,
    GetTrainerAffiliationDTO
)
from datetime import datetime
import pytz
from utils.image_management import generate_image_urls, generate_image_url
from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles
from data.dbapis.trainer_affiliation import save_trainer_affiliation, find_many_trainer_affiliations, \
    find_trainer_affiliation
import phonenumbers

clubs_api_router = APIRouter(
    prefix="/clubs",
    tags=["clubs"]
)


@clubs_api_router.put("/update-club")
async def update_club(
        request: Request,
        update_club_parameter_control: Annotated[
            UpdateClubParameterControl,
            Depends()
        ]
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
        **update_club_request.model_dump(exclude_unset=True)
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
            "updated_club": GetClub(
                logo=generate_image_url(image_id=updated_club.logo, request=request),
                images=generate_image_urls(image_ids=updated_club.images, request=request),
                **updated_club.model_dump(exclude={"logo", "images"})
            )}
    )


@clubs_api_router.get("/get-club/{club_id}")
async def get_club_by_id(
        request: Request,
        club_id: str,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /clubs/get-club/{club_id} (club_id={club_id}, user_id={user.id})")

    club = find_club(id=club_id)

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no club exists with the provided id (club_id={club_id})"
        )

    retval = Success(
        message="club retrieved successfully...",
        data=GetClubDetailedDTO(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-clubs")
async def get_clubs(
        request: Request,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /clubs/get-clubs (user_id={user.id})")

    clubs = find_many_clubs()

    retval = Success(
        message="club retrieved successfully...",
        data=[
            GetClub(
                logo=generate_image_url(image_id=club.logo, request=request),
                images=generate_image_urls(image_ids=club.images, request=request),
                **club.model_dump(exclude={"logo", "images"})
            ) for club in clubs
        ]
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-your-club")
async def get_your_club(
        request: Request,
        user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.CLUB}))
        ]
):
    log.info(f"inside /clubs/get-your-club (user_id={user.id})")

    club = find_club_by_user(user_id=str(user.id))

    retval = Success(
        message="club retrieved successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-logo")
async def upload_logo(
        request: Request,
        logo: UploadFile,
        club_id_parameter_control: Annotated[
            ClubIdParameterControlForm,
            Depends()
        ]
):
    user = club_id_parameter_control.user
    club_id = club_id_parameter_control.club_id

    log.info(f"inside /clubs/upload-logo(user_id={user.id}, club_id={club_id})")

    club = await upload_logo_logic(
        club_id=club_id,
        logo=logo
    )

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-images")
async def upload_logo(
        request: Request,
        images: list[UploadFile],
        club_id_parameter_control: Annotated[
            ClubIdParameterControlForm,
            Depends()
        ]
):
    user = club_id_parameter_control.user
    club_id = club_id_parameter_control.club_id

    log.info(f"inside /clubs/upload-images(user_id={user.id}, club_id={club_id})")

    club = await upload_images_logic(
        club_id=club_id,
        images=images
    )

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/generate-trainer-affiliation")
async def generate_trainer_affiliation(
        generate_trainer_affiliation_dto: GenerateTrainerAffiliationDTO,
        club_id_parameter_control: Annotated[
            ClubIdParameterControlBody,
            Depends()
        ]
):
    user = club_id_parameter_control.user
    club_id = club_id_parameter_control.club_id

    log.info(f"inside /clubs/generate-trainer-affiliation (user={user}, club_id={club_id})")

    new_trainer_affiliation = TrainerAffiliationInternal(
        created_by=user.id,
        club_id=club_id,
        **generate_trainer_affiliation_dto.model_dump()
    )

    trainer_affiliation = save_trainer_affiliation(new_trainer_affiliation=new_trainer_affiliation)

    retval = Success(
        message="trainer affiliation number generated successfully",
        data=GetTrainerAffiliationDTO(**trainer_affiliation.model_dump())
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-trainer-affiliation")
async def get_trainer_affiliation(
        user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.CLUB}))
        ],
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
):
    log.info(f"inside /clubs/get-trainer-affiliation (user_id={user.id}, email_address={email_address}, "
             f"phone_number={phone_number})")

    club = find_club_by_user(user_id=str(user.id))

    # TODO: design a generic query dbapi with filtering, ordering and pagination and replace the following code

    formatted_phone_number = None

    if phone_number:
        phone_number_error = ValueError(f"invalid phone number (phone_number={phone_number})")

        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            log.info(f"failed to parse phone number, raising error (phone_number={phone_number})")
            raise phone_number_error

        formatted_phone_number = phonenumbers.format_number(
            parsed_phone_number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

    filter_dict = {"club_id": str(club.id)}

    if email_address:
        filter_dict["email_address"] = email_address

    if formatted_phone_number:
        filter_dict["phone_number"] = formatted_phone_number

    trainer_affiliation_list = find_many_trainer_affiliations(**filter_dict)

    retval = Success(
        message="trainer affiliation numbers fetched successfully...",
        data=[
            GetTrainerAffiliationDTO(**trainer_affiliation.model_dump())
            for trainer_affiliation in trainer_affiliation_list
        ]
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-your-affiliation-number")
async def get_your_affiliation(
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /clubs/get-your-trainer-affiliation-number (user_id={user.id})")

    trainer_affiliation = find_trainer_affiliation(phone_number=user.phone_number)

    retval = Success(
        message="trainer_affiliation_number found for the user",
        data=GetTrainerAffiliationDTO(**trainer_affiliation.model_dump())
    ) if trainer_affiliation else Success(
        message="no trainer_affiliation_number found for the user"
    )

    log.info(f"returning {retval}")

    return retval
