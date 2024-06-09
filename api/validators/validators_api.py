from fastapi import APIRouter, HTTPException, status
from typing import Optional
from models.validators import ValidationResponse
from logging_config import log
from validators.user import whether_user_exists

validators_api_router = APIRouter(
    prefix="/validators",
    tags=["validators"]
)


@validators_api_router.get("/whether-user-exists")
async def whether_user_exists_api(
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None
) -> ValidationResponse:
    log.info(f"/validators/whether-user-exists (email_address={email_address}, phone_number={phone_number})")

    if email_address and phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone should be passed not both"
        )

    if not (email_address or phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone must be passed"
        )

    result = whether_user_exists(email=email_address, phone=phone_number)

    return ValidationResponse(
        valid=result,
        message="a true value for `valid` implies that a user already exists for the given email/phone"
    )
