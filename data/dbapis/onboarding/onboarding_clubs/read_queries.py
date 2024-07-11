from data.db import get_clubs_collection

clubs_collection = get_clubs_collection()


def get_clubs():
    clubs = clubs_collection.find({})
    return list(clubs)
