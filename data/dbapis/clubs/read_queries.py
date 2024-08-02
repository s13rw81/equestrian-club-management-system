from typing import Optional, List

from bson.errors import InvalidId
from bson.objectid import ObjectId
from data.db import get_clubs_collection
from logging_config import log
from models.clubs import ClubInternal

club_collection = get_clubs_collection()


def get_all_clubs_logic() -> Optional[List[Optional[ClubInternal]]]:
    """
        get all the clubs instances
        :returns: all of clubs as list of dicts
    """

    log.info(f"get_all_clubs invoked")
    # # clubs = [club for club in (await club_collection.find())]
    # # retval = UserInternal(**user, id = str(user['_id']))
    # all_clubs = club_collection.find({})
    # clubs = list()
    # for club in all_clubs:
    #     clubs.append(ClubInternal(**club))
    # log.info(f"returning {clubs}")
    # return clubs
    # Aggregation pipeline
    pipeline = [
        {
            '$addFields': {
                '_id_str': {'$toString': '$_id'}
            }
        },
        {
            '$lookup': {
                'from': 'reviews',
                'localField': '_id_str',
                'foreignField': 'reviewee.reviewee_id',
                'as': 'reviews'
            }
        },
        {
            '$addFields': {
                'average_rating': {
                    '$cond': {
                        'if': {'$gt': [{'$size': '$reviews'}, 0]},
                        'then': {'$avg': '$reviews.rating'},
                        'else': None
                    }
                }
            }
        },
        {
            '$project': {
                '_id_str': 0
            }
        }
    ]

    # Execute the aggregation pipeline
    clubs_with_ratings = list(club_collection.aggregate(pipeline))
    for club in clubs_with_ratings:
        club['id'] = str(club['_id'])
    return clubs_with_ratings
    # # Print clubs with average ratings
    # for club in clubs_with_ratings:
    #     print(club)


def get_club_by_id_logic(club_id: str) -> ClubInternal | None:
    """
    :param club_id: id of the club to be fetched
    :return: instance of ClubInternal, details of the club
    """

    club = None

    # fetch the club
    try:
        club = club_collection.find_one({"_id": ObjectId(club_id)})
    except InvalidId as e:
        log.error(f'{e} :  club_id')
    finally:
        return club


def get_club_with_services_and_trainer(club_id: str):
    club_id = ObjectId(club_id)

    pipeline = [
        {
            '$match': {'_id': club_id}
        },
        {
            '$addFields': {
                '_id_str': {'$toString': '$_id'}
            }
        },
        {
            '$lookup': {
                'from': 'generic_activity_service',
                'localField': '_id_str',
                'foreignField': 'provider.provider_id',
                'as': 'generic_activity_service'
            }
        },
        {
            '$lookup': {
                'from': 'horse_shoeing_service',
                'localField': '_id_str',
                'foreignField': 'provider.provider_id',
                'as': 'horse_shoeing_service'
            }
        },
        {
            '$lookup': {
                'from': 'riding_lesson_service',
                'localField': '_id_str',
                'foreignField': 'provider.provider_id',
                'as': 'riding_lesson_service'
            }
        },
        {
            '$lookup': {
                'from': 'trainer',
                'localField': '_id_str',
                'foreignField': 'club_id',
                'as': 'trainers'
            }
        },
        {
            '$lookup': {
                'from': 'reviews',
                'localField': '_id_str',
                'foreignField': 'reviewee.reviewee_id',
                'as': 'reviews'
            }
        },
        {
            '$addFields': {
                'average_rating': {
                    '$cond': {
                        'if': {'$gt': [{'$size': '$reviews'}, 0]},
                        'then': {'$avg': '$reviews.rating'},
                        'else': None
                    }
                }
            }
        }
    ]

    club_data = list(club_collection.aggregate(pipeline))

    return club_data[0] if club_data else None
