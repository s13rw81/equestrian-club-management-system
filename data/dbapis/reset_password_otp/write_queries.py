from data.db import get_reset_password_otp_collection
from logging_config import log
from models.reset_password_otp import ResetPasswordOtpInternal, UpdateResetPasswordOtpInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from . import find_reset_password_otp

reset_password_otp_collection = get_reset_password_otp_collection()


@atomic_transaction
def save_reset_password_otp(
        new_reset_password_otp: ResetPasswordOtpInternal,
        session=None
) -> ResetPasswordOtpInternal:

    log.info(f"inside save_reset_password_otp(reset_password_otp={new_reset_password_otp})")

    result = reset_password_otp_collection.insert_one(new_reset_password_otp.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new reset_password_otp can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new reset_password_otp can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new reset_password_otp has successfully been inserted ("
             f"reset_password_otp_id={new_reset_password_otp.id})")

    return new_reset_password_otp


@atomic_transaction
def update_reset_password_otp(
        update_reset_password_otp_dto: UpdateResetPasswordOtpInternal,
        session=None
) -> ResetPasswordOtpInternal:
    log.info(f"inside update_reset_password_otp(update_reset_password_otp_dto={update_reset_password_otp_dto})")

    reset_password_otp_database_id = str(update_reset_password_otp_dto.id)

    update_reset_password_otp_dict = update_reset_password_otp_dto.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": reset_password_otp_database_id}

    result = reset_password_otp_collection.update_one(
        update_filter,
        {"$set": update_reset_password_otp_dict},
        session=session
    )

    log.info(
        f"reset_password_otp update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update the reset_password_otp due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="sign_up_otp cannot be updated in the database due to unknown reasons"
        )

    updated_reset_passwrd_otp = find_reset_password_otp(id=reset_password_otp_database_id, session=session)

    return updated_reset_passwrd_otp
