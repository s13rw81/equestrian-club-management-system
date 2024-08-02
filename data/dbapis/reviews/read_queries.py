from data.db import get_reviews_collection

reviews_collection = get_reviews_collection()


def get_review_by_reviewer_for_reviewee(reviwer: str, reviewee: str):
    query = {
        'reviewee.reviewee_id': reviewee,
        'reviewer.reviewer_id': reviwer
    }
    return reviews_collection.find_one(query)
