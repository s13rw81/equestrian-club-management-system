from fastapi import APIRouter, Depends, UploadFile
from typing import Annotated
from models.http_responses import Success
from .models import (
    GetTrainerDetailedDTO,
    GetTrainerCertificationDTO
)
from .role_based_parameter_control import (
    GetTrainersPaginatedParamCtrl,
    TrainerCertIdParamCtrlForm
)
from logging_config import log
from logic.trainers import (
    trainers_get_query_with_pagination,
    upload_trainer_certificate_image
)

trainers_api_router = APIRouter(
    prefix="/trainers",
    tags=["trainers"]
)


@trainers_api_router.get("/get-trainers-paginated")
async def get_trainers_paginated(
        get_trainers_param_ctrl: Annotated[
            GetTrainersPaginatedParamCtrl,
            Depends()
        ]
):
    user = get_trainers_param_ctrl.user
    get_query_paginated_dto = get_trainers_param_ctrl.get_query_paginated_dto

    f = get_query_paginated_dto.f
    s = get_query_paginated_dto.s
    page_no = get_query_paginated_dto.page_no
    page_size = get_query_paginated_dto.page_size

    log.info("inside /trainers/get-trainers-paginated ("
             f"f={f}, s={s}, page_no={page_no}, page_size={page_size}, user_id={user.id})")

    result = trainers_get_query_with_pagination(
        f=f, s=s, page_no=page_no, page_size=page_size
    )

    log.info(f"received data = {result}")

    retval = Success(
        message="trainer details fetched successfully",
        data=[GetTrainerDetailedDTO(**data.model_dump()) for data in result]
    )

    log.info(f"returning {retval}")

    return retval


@trainers_api_router.post("/upload-certification-image")
async def upload_certification_image(
        image: UploadFile,
        trainer_cert_id_param_ctrl: Annotated[
            TrainerCertIdParamCtrlForm,
            Depends()
        ]
):
    log.info(f"inside upload-trainer-certification-image("
             f"trainer_certification_id={trainer_cert_id_param_ctrl.trainer_certification_id}), "
             f"image_filename={image.filename}, "
             f"user_id={trainer_cert_id_param_ctrl.user.id}")

    trainer_certification = await upload_trainer_certificate_image(
        certificate_id=trainer_cert_id_param_ctrl.trainer_certification_id,
        image=image
    )

    retval = Success(
        message="successfully saved trainer_certification_image",
        data=GetTrainerCertificationDTO(**trainer_certification.model_dump())
    )

    log.info(f"returning {retval}")

    return retval





# @trainers_api_router.put("/update-trainer")
# async def update_trainer(
#         update_trainer_parameter_control: Annotated[
#             UpdateTrainerParameterControl,
#             Depends()
#         ]
# ):
#     update_trainer_dto = update_trainer_parameter_control.update_trainer_dto
#     user = update_trainer_parameter_control.user
#
#     log.info(
#         f"inside /trainers/update-trainer ("
#         f"update_trainer_dto={update_trainer_dto}, "
#         f"user={user})"
#     )
#
#     update_trainer_dto = UpdateTrainerInternal(
#         id=update_trainer_dto.id,
#         last_updated_by=user.id,
#         last_update_on=datetime.now(pytz.utc),
#         **update_trainer_dto.model_dump(exclude_unset=True)
#     )
#
#
#     updated_trainer = update_trainer_db(update_trainer_dto=update_trainer_dto)
#
#     log.info("trainer updated successfully, returning...")
#
#     return Success(
#         message="trainer updated successfully...",
#         data={
#             "updated_trainer": GetTrainerDTO(**updated_trainer.model_dump())
#         }
#     )
#
#
# @trainers_api_router.get("/get-trainer/{trainer_id}")
# async def get_trainer_by_id(
#         trainer_id: str,
#         user: Annotated[UserInternal, Depends(get_current_user)]
# ):
#     log.info(f"inside /trainers/get-trainer/{trainer_id} (club_id={trainer_id}, user_id={user.id})")
#
#     trainer = find_trainer(id=trainer_id)
#
#     if not trainer:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"no trainer exists with the provided id (trainer_id={trainer_id})"
#         )
#
#     retval = Success(
#         message="trainer retrieved successfully...",
#         data=GetTrainerDTO(**trainer.model_dump())
#     )
#
#     log.info(f"returning {retval}")
#
#     return retval
#
#
# @trainers_api_router.get("/get-your-trainer")
# async def get_your_trainer(
#         user: Annotated[
#             UserInternal,
#             Depends(RoleBasedAccessControl(allowed_roles={UserRoles.TRAINER}))
#         ]
# ):
#     log.info(f"inside /trainers/get-your-trainer (user_id={user.id})")
#
#     trainer = find_trainer(user_id=str(user.id))
#
#     retval = Success(
#         message="trainer retrieved successfully...",
#         data=GetTrainerDTO(**trainer.model_dump())
#     )
#
#     log.info(f"returning {retval}")
#
#     return retval
#
# @trainers_api_router.get("/get-trainers-by-club/{club_id}")
# async def get_trainers_by_club(
#         club_id: str,
#         user: Annotated[
#             UserInternal,
#             Depends(get_current_user)
#         ]
# ):
#     log.info(f"inside /trainers/get-trainers-by-club/{club_id} (club_id={club_id}, user_id={user.id})")
#
#     trainers = find_many_trainers(club_affiliation=club_id)
#
#     retval = Success(
#         message="trainers retrieved successfully...",
#         data=[
#             GetTrainerDTO(**trainer.model_dump()) for trainer in trainers
#         ]
#     )
#
#     log.info(f"returning {retval}")
#
#     return retval
