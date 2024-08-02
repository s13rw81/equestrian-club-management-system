from api.clubs.models.ratings_request_model import ClubReview
from data.dbapis.clubs import get_club_by_id_logic
from data.dbapis.reviews.read_queries import get_review_by_reviewer_for_reviewee
from data.dbapis.reviews.write_queries import create_review_for_club_by_user
from fastapi import HTTPException
from logging_config import log
from models.reviews.reviews import Review, Reviewee, Reviewer
from models.user import UserInternal, UserRoles
from starlette import status


def check_existing_review_by_user_for_club(club_review: ClubReview, user: UserInternal):
    club_review_dict = club_review.model_dump(exclude_none=True)
    club_id = club_review_dict['club_id']
    # check if club exists
    res = get_club_by_id_logic(club_id=club_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'club with id {club_id} not found.')
    user_id = user.id
    res = get_review_by_reviewer_for_reviewee(reviwer=user_id, reviewee=club_id)
    log.info(f'get_review_by_reviewer_for_reviewee :  {get_review_by_reviewer_for_reviewee}')
    return res


def add_review_for_club_by_user(club_review: ClubReview, user: UserInternal):
    reviewee_instance = Reviewee(
        reviewee_id=club_review.club_id,
        reviewee_type=UserRoles.CLUB
    )
    reviewer_instance = Reviewer(
        reviewer_id=user.id,
        reviewer_type=UserRoles.USER
    )
    review_instance = Review(
        reviewee=reviewee_instance,
        reviewer=reviewer_instance,
        rating=club_review.rating,
        review=club_review.review,
    )

    res = create_review_for_club_by_user(review_instance.model_dump(exclude_none=True))
    return res
