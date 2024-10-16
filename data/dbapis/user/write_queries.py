from data.db import get_users_collection
from logging_config import log
from models.user import UpdateUserInternal, UserInternal
from .read_queries import find_user
from fastapi import HTTPException, status
from decorators import atomic_transaction

users_collection = get_users_collection()


@atomic_transaction
def save_user(user: UserInternal, session=None) -> UserInternal:

    log.info(f"save_user invoked: {user}")

    result = users_collection.insert_one(user.model_dump(), session=session)

    if not result.acknowledged:
        log.info("new user can't be inserted in the database, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="new user can't be inserted in the database due to unknown reasons..."
        )

    log.info(f"new user has successfully been inserted (user_id={user.id})")

    return user

@atomic_transaction
def update_user(update_user_dto: UpdateUserInternal, session=None) -> UserInternal:
    log.info(f"inside update_user(update_user_dto={update_user_dto})")

    user_database_id = str(update_user_dto.id)

    update_user_dict = update_user_dto.model_dump(exclude={"id"}, exclude_unset=True)

    update_filter = {"id": user_database_id}

    result = users_collection.update_one(
        update_filter,
        {"$set": update_user_dict},
        session=session
    )

    log.info(
        f"user update executed, matched_count={result.matched_count}, "
        f"modified_count={result.modified_count}"
    )

    if not result.modified_count:
        log.info("could not update the user due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="user cannot be updated in the database due to unknown reasons"
        )

    updated_user = find_user(id=user_database_id, session=session)

    return updated_user

