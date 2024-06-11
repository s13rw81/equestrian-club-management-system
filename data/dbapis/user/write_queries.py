from data.db import get_users_collection
from logging_config import log
from models.user import UserInternal, UpdateUserInternal, SignUpCredentialType

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


def update_user(update_user_data: UpdateUserInternal, user: UserInternal) -> bool:
    """
        updates the user as per the data provided in the edit_user dict

        :param update_user_data: UpdateUserInternal
        :param user: str

        :returns: True if successfully updated false otherwise

    """

    log.info(f"inside update_user(update_user_data={update_user_data}, user={user})")

    update_user_dict = update_user_data.model_dump(exclude_none=True)

    update_filter = ({"email_address": user.email_address}
                     if user.sign_up_credential_type == SignUpCredentialType.EMAIL_ADDRESS
                     else {"phone_number": user.phone_number})

    result = users_collection.update_one(
        update_filter,
        {"$set": update_user_dict, "$currentDate": {"lastModified": True}}
    )

    log.info(f"matched_count={result.matched_count}, modified_count={result.modified_count}")

    return result.modified_count == 1
