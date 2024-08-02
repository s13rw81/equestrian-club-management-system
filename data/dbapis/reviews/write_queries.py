from data.db import get_reviews_collection

reviews_collection = get_reviews_collection()


def create_review_for_club_by_user(review_instance):
    return reviews_collection.insert_one(review_instance)
