from data.db import get_sign_up_otp_collection
from logging_config import log
from models.sign_up_otp import SignUpOtpInternal, UpdateSignUpOtpInternal
from fastapi import HTTPException, status
from decorators import atomic_transaction
from . import find_sign_up_otp

sign_up_otp_collection = get_sign_up_otp_collection()


@atomic_transaction
def save_sign_up_otp(new_sign_up_otp: SignUpOtpInternal, session=None) -> SignUpOtpInternal:

    log.info(f"inside save_sign_up_otp(sign_up_otp={new_sign_up_otp})")

    result = sign_up_otp_collection.insert_one(new_sign_up_otp.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new sign_up_otp can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new sign_up_otp can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new sign_up_otp has successfully been inserted (sign_up_otp_id={new_sign_up_otp.id})")

    return new_sign_up_otp


@atomic_transaction
def update_sign_up_otp(update_sign_up_otp_data: UpdateSignUpOtpInternal, session=None) -> SignUpOtpInternal:
    log.info(f"inside update_club(update_sign_up_otp_data={update_sign_up_otp_data})")

    sign_up_otp_database_id = update_sign_up_otp_data.id.hex

    update_sign_up_otp_dict = update_sign_up_otp_data.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": sign_up_otp_database_id}

    result = sign_up_otp_collection.update_one(
        update_filter,
        {"$set": update_sign_up_otp_dict},
        session=session
    )

    log.info(
        f"sign_up_otp update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update the sign_up_otp due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="sign_up_otp cannot be updated in the database due to unknown reasons"
        )

    updated_sign_up_otp = find_sign_up_otp(id=sign_up_otp_database_id, session=session)

    return updated_sign_up_otp
