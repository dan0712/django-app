import datetime

from main.models import ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_JOINT, ACCOUNT_TYPE_SMSF


def years_between(first, second):
    return int((second - first).days / 365.25)


def recommend_risk(setting):
    """
    Recommend a risk score for the given goal setting
    :param setting: The goal setting to build the recommedation for
    :return: A Float [0-1]
    """
    # If the account is a Joint or Personal, use age of youngest owner, otherwise, use None
    account = setting.goal.account
    today = datetime.datetime.today()
    if account.account_type in (ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_JOINT):
        primary_owner = account.primary_owner
        age = years_between(primary_owner.date_of_birth, today)
        income = primary_owner.income
        worth = primary_owner.worth
        if account.account_type == ACCOUNT_TYPE_JOINT:
            joint_holder = account.joint_holder.client
            age2 = years_between(joint_holder.date_of_birth, today)
            age = min(age, age2)
            income += joint_holder.income
            worth += joint_holder.worth

        # TODO: Maybe we want the "best" status, or maybe the status of the youngest?, Or maybe an average.
        status = primary_owner.employment_status
    else:
        age = None
        status = None
        income = None
        # TODO: For trusts, use the trust assets as worth
        worth = None

    ttl = years_between(today, setting.completion)
    risk_sensitivity = setting.goal.type.risk_sensitivity

    return get_recommendation(age, status, income, worth, ttl, risk_sensitivity)


def get_recommendation(age, status, income, worth, ttl, risk_sensitivity):
    """
    Get a recommended risk score (0-100) based on some characteristics of a goal.
    :param age:
    :param status:
    :param income:
    :param worth:
    :param ttl:
    :param risk_sensitivity:
    :return: A recommended risk score.
    """
    # TODO: Make it work
    return 0.5