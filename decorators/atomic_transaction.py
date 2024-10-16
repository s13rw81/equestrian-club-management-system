from functools import wraps
from data.db import client
from pymongo import errors

def atomic_transaction(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        # If session is provided, then func is not an initiator function in the transaction chain.
        is_session_provided = "session" in kwargs

        # If session is not provided, then func is an initiator function.
        # Initiator functions are responsible for starting the transaction as well as aborting it
        # in cases of exceptions.
        if not is_session_provided:
            session = client.start_session()
            session.start_transaction()
            kwargs["session"] = session

        try:
            retval = func(*args, **kwargs)

        except (errors.PyMongoError, Exception) as e:

            if not is_session_provided:
                session.abort_transaction()
                session.end_session()

            raise e


        if not is_session_provided:
            session.commit_transaction()
            session.end_session()

        return retval

    return wrapper





