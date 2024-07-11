from data.db import get_logistics_company_collection

logistic_companies_collection = get_logistics_company_collection()


def get_logistic_companies():
    companies = logistic_companies_collection.find({})
    return list(companies)
