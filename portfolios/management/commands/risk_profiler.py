import datetime

import math

from main.models import ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_JOINT, ACCOUNT_TYPE_SMSF, EMPLOYMENT_STATUS_FULL_TIME, \
    EMPLOYMENT_STATUS_PART_TIME, EMPLOYMENT_STATUS_STUDENT, EMPLOYMENT_STATUS_RETIRED, EMPLOYMENT_STATUS_HOMEMAKER, \
    EMPLOYMENT_STATUS_UNEMPLOYED, EMPLOYMENT_STATUS_SELF_EMPLOYED

# Risk tolerance scores for each employment status
EMPLOYMENT_STATUS_SCORES = {
    EMPLOYMENT_STATUS_FULL_TIME: 8,
    EMPLOYMENT_STATUS_PART_TIME: 6,
    EMPLOYMENT_STATUS_SELF_EMPLOYED: 7,
    EMPLOYMENT_STATUS_STUDENT: 10,
    EMPLOYMENT_STATUS_RETIRED: 1,
    EMPLOYMENT_STATUS_HOMEMAKER: 5,
    EMPLOYMENT_STATUS_UNEMPLOYED: 1,
}

LOW_LEVEL_INCOME = 10000
HIGH_LEVEL_INCOME = 200000

LOW_LEVEL_WORTH = 10000
HIGH_LEVEL_WORTH = 1000000


def years_between(first, second):
    return int((second - first).days / 365.25)


def recommend_risk(setting):
    """
    Recommend a risk score for the given goal setting
    :param setting: The goal setting to build the recommedation for
    :return: A Float [0-1]
    """
    age, goal_type_sensitivity, income, status, ttl, worth = get_setting_params(setting)

    return get_recommendation(age, status, income, worth, ttl, goal_type_sensitivity)


def recommend_ttl_risks(setting, years):
    """
    Generates a list of recommended risk scores for the number of years given.
    Eg. if years is 3, a list len 3 is returned for risk given 1 year, 2 years and 3 years ttl.
    :param setting: The setting to get the details from
    :param years: The number of year options to use.
    :return: A list of floats.
    """
    age, goal_type_sensitivity, income, status, _, worth = get_setting_params(setting)
    return [get_recommendation(age, status, income, worth, ttl, goal_type_sensitivity) for ttl in range(1, years+1)]


def get_setting_params(setting):
    # If the account is a Joint or Personal, use age of youngest owner, otherwise, use None
    account = setting.goal.account
    today = datetime.datetime.today().date()
    if account.account_type in (ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_JOINT):
        primary_owner = account.primary_owner
        age = years_between(primary_owner.date_of_birth, today)
        income = primary_owner.income
        worth = primary_owner.net_worth
        if account.account_type == ACCOUNT_TYPE_JOINT:
            joint_holder = account.joint_holder.client
            age2 = years_between(joint_holder.date_of_birth, today)
            age = min(age, age2)
            income += joint_holder.income
            worth += joint_holder.net_worth

        # TODO: Maybe we want the "best" status, or maybe the status of the youngest?, Or maybe an average.
        status = primary_owner.employment_status
    else:
        age = None
        status = None
        income = None
        # TODO: For trusts, use the trust assets as worth
        worth = None
    ttl = years_between(today, setting.completion)
    goal_type_sensitivity = setting.goal.type.risk_sensitivity

    return age, goal_type_sensitivity, income, status, ttl, worth


def get_recommendation(age, status, income, worth, ttl, goal_type_sensitivity):
    """
    Get a recommended risk score (0-100) based on some characteristics of a goal.
    :param age:
    :param status:
    :param income:
    :param worth:
    :param ttl: The number of years left to go before this goal matures.
    :param goal_type_sensitivity: 0 = not sensitive to risk, 10 = very sensitive to risk
    :return: A recommended risk score as a float between 0 and 1
    """

    # Anyone age 20 or under gets a score of 10, otherwise it scales down to 0 at age 95,
    # slightly negative any older than that.
    if age is None:
        age_score = 10
    else:
        age_score = 10*(1-max(0,age-20)/(95-20))

    if status is None:
        status_score = 10
    else:
        status_score = EMPLOYMENT_STATUS_SCORES[status]

    if income is None:
        income_score = 10  # Roughly equivalent to 500k
    else:
        income_score = max(0, math.log(max(1, income)/LOW_LEVEL_INCOME, (HIGH_LEVEL_INCOME/LOW_LEVEL_INCOME) ** (1/8)))

    if worth is None:
        worth_score = 10  # Roughly 3.5M with 10K/1M settings
    else:
        worth_score = max(0, math.log(max(1, worth)/LOW_LEVEL_WORTH, (HIGH_LEVEL_WORTH/LOW_LEVEL_WORTH) ** (1/8)))

    ttl_score = 10 if ttl > 15 else 8 if ttl > 10 else ttl/1.5

    return min(1.0, ((10 - goal_type_sensitivity) + age_score + status_score + income_score + worth_score + ttl_score) / 90)
