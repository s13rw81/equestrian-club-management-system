from api.user.models import UpdateUserRole
from bson import ObjectId
from logging_config import log
from logic.onboarding.logistics import users_collection
from models.user import UserInternal


def upgrade_user_role(user_update_request: UpdateUserRole, user: UserInternal):
    update_user_dict = user_update_request.model_dump(exclude_none=True)

    update_filter = {"email_address": user.email_address}

    result = users_collection.update_one(update_filter, {"$set": {'user_role': update_user_dict['user_role'].value}})

    log.info(f"matched_count={result.matched_count}, modified_count={result.modified_count}")

    return result.modified_count == 1
