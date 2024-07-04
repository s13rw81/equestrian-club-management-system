from data.db import get_clubs_collection


def check_club_email_exists(email):
    clubs_collection = get_clubs_collection()
    if clubs_collection.find_one({"email_address": email}):
        return True
    return False
