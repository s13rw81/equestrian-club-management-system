from data.db import get_logistics_company_collection


def check_logistic_company_email_exists(email):
    logistics_company_collection = get_logistics_company_collection()
    if logistics_company_collection.find_one({"email_address": email}):
        return True
    return False
