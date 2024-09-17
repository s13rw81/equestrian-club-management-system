from data.db import convert_to_object_id, get_users_collection
from logging_config import log
from models.user import SignUpCredentialType, UpdateUserInternal, UserInternal
from models.user.enums.user_roles import UserRoles
from fastapi import HTTPException, status
from decorators import atomic_transaction

users_collection = get_users_collection()


def save_user(user: UserInternal) -> str:
    """
    saves the new user in the database and returns the id

    :param user: InternalUser

    :returns: id
    """

    log.info(f"save_user invoked: {user}")

    user_id = (users_collection.insert_one(user.model_dump())).inserted_id

    retval = str(user_id)

    log.info(f"returning {retval}")

    return retval

@atomic_transaction
def update_user(update_user_data: UpdateUserInternal, user: UserInternal, session=None) -> bool:
    """
    updates the user as per the data provided in the edit_user dict

    :param update_user_data: UpdateUserInternal
    :param user: str
    :param session: database transaction session

    :returns: True if successfully updated. :raises: HttpException on failure of update.

    """

    log.info(f"inside update_user(update_user_data={update_user_data}, user={user})")

    update_user_dict = update_user_data.model_dump(exclude_none=True)

    update_filter = (
        {"email_address": user.email_address}
        if user.sign_up_credential_type == SignUpCredentialType.EMAIL_ADDRESS
        else {"phone_number": user.phone_number}
    )

    result = users_collection.update_one(
        update_filter,
        {"$set": update_user_dict, "$currentDate": {"lastModified": True}},
        session=session
    )

    log.info(
        f"user update executed matched_count={result.matched_count}, modified_count={result.modified_count}"
    )

    if not result.modified_count == 1:
        log.info("could not update user due to unknown reasons, raising exception")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="user cannot be updated in the database due to unknown reasons"
        )

    return True


def update_user_role(user_role: UserRoles, user: UserInternal) -> bool:
    """updates the role of a particular user to user_role

    Args:
        user_role (_type_): _description_
        user (UserInternal): _description_

    Returns:
        bool: _description_
    """

    filter = {"_id": convert_to_object_id(user.id)}
    result = users_collection.update_one(
        filter=filter, update={"$set": {"user_role": user_role.value}}
    )

    return result.modified_count == 1
