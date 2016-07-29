import math

from django.db.models.aggregates import Max, Min, Sum
from django.utils.timezone import now

from client.models import RiskProfileAnswer
from main.constants import ACCOUNT_TYPE_JOINT, ACCOUNT_TYPE_PERSONAL, \
    ACCOUNT_TYPE_SMSF, EMPLOYMENT_STATUS_FULL_TIME, \
    EMPLOYMENT_STATUS_HOMEMAKER, EMPLOYMENT_STATUS_PART_TIME, \
    EMPLOYMENT_STATUS_RETIRED, EMPLOYMENT_STATUS_SELF_EMPLOYED, \
    EMPLOYMENT_STATUS_STUDENT, EMPLOYMENT_STATUS_UNEMPLOYED

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

# The risk score if we don't have enough info to say anything.
NEUTRAL_RISK = 0.5


def years_between(first, second):
    return int((second - first).days / 365.25)


def recommend_risk(setting):
    """
    Recommend a risk score for the given goal setting
    :param setting: The goal setting to build the recommedation for
    :return: A Float [0-1]
    """
    weights, age, income, status, ttl, worth = get_risk_factors(setting)

    return get_risk_score(get_risk_ability(age, status, income, worth, ttl, weights),
                          get_risk_willingness(setting.goal.account))


def recommend_ttl_risks(setting, years):
    """
    Generates a list of recommended risk scores for the number of years given.
    Eg. if years is 3, a list len 3 is returned for risk given 1 year, 2 years and 3 years ttl.
    :param setting: The setting to get the details from
    :param years: The number of year options to use.
    :return: A list of floats.
    """
    weights, age, income, status, _, worth = get_risk_factors(setting)
    risk_willingness = get_risk_willingness(setting.goal.account)
    return [get_risk_score(get_risk_ability(age, status, income, worth, ttl, weights),
                           risk_willingness)
            for ttl in range(1, years + 1)]


def get_risk_factors(setting):
    # If the account is a Joint or Personal, use age of youngest owner, otherwise, use None
    account = setting.goal.account
    today = now().date()
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
        status = EMPLOYMENT_STATUS_UNEMPLOYED if primary_owner.employment_status is None else primary_owner.employment_status
    else:
        age = None
        status = None
        income = None
        # TODO: For trusts, use the trust assets as worth
        worth = None
    ttl = max(0, years_between(today, setting.completion))
    weights = setting.goal.type.risk_factor_weights

    return weights, age, income, status, ttl, worth


def get_risk_willingness(account):
    """
    Get the score [0-1] for an entity's willingness to take risk, based on a previous elicitation of its preferences.
    :return:
    """
    if not hasattr(account.risk_profile_group, 'questions'):
        # No risk questions assigned, so we can't say anything about their willingness to take risk.
        return NEUTRAL_RISK
    qids = set(account.risk_profile_group.questions.all().values_list('id', flat=True))
    if len(qids) == 0:
        # No risk questions assigned, so we can't say anything about their willingness to take risk.
        return NEUTRAL_RISK

    if not account.risk_profile_responses:
        # No risk responses give, so we can't say anything about their willingness to take risk.
        return NEUTRAL_RISK

    aqs = account.risk_profile_responses.all()
    if not qids == set(aqs.values_list('question_id', flat=True)):
        # Risk responses are not complete, so we can't say anything about their willingness to take risk.
        return NEUTRAL_RISK

    # Get the min and max score possible for the group
    extents = (
        RiskProfileAnswer.objects.filter(question__group=account.risk_profile_group)  # All answers for the group
        .values('question').annotate(min_score=Min('score'), max_score=Max('score'))  # Group by question
        .aggregate(min=Sum('min_score'), max=Sum('max_score'))  # Get min and max total score
    )

    # Scale the actual score to wherever it fits between the min and max [0-1].
    # If there is no range, the questions are bad, so just return 0.5
    rng = (extents['max'] - extents['min'])
    return NEUTRAL_RISK if rng == 0 else (aqs.aggregate(total=Sum('score'))['total'] - extents['min']) / rng


def get_risk_ability(age, status, income, worth, ttl, weights):
    """
    Get the score [0-1] for an entity's ability to take risk, based on their financial profile.
    :param age:
    :param status:
    :param income:
    :param worth:
    :param ttl: The number of years left to go before this goal matures.
    :param weights: The weights for each of the factors, as a dict from param name to weight.
    :return: A risk ability score as a float between 0 and 1
    """

    max_total = 0

    # Anyone age 20 or under gets a score of 10, otherwise it scales down to 0 at age 95,
    # slightly negative any older than that.
    if age is not None and weights and 'age' in weights:
        age_score = weights['age']*10*(1-max(0, age-20)/(95-20))
        max_total += weights['age']

    if status is not None and weights and 'status' in weights:
        status_score = weights['status']*EMPLOYMENT_STATUS_SCORES[status]
        max_total += weights['status']

    if income is not None and weights and 'income' in weights:
        income_score = weights['income']*max(0, math.log(max(1, income)/LOW_LEVEL_INCOME,
                                                         (HIGH_LEVEL_INCOME/LOW_LEVEL_INCOME) ** (1/8)))
        max_total += weights['income']

    if worth is not None and weights and 'worth' in weights:
        worth_score = weights['worth']*max(0, math.log(max(1, worth)/LOW_LEVEL_WORTH,
                                                       (HIGH_LEVEL_WORTH/LOW_LEVEL_WORTH) ** (1/8)))
        max_total += weights['worth']

    if weights and 'age' in weights:
        ttl_score = weights['ttl']*(10 if ttl > 15 else 8 if ttl > 10 else ttl/1.5)
        max_total += weights['ttl']

    return NEUTRAL_RISK if max_total == 0 else min(1.0, (age_score + status_score + income_score + worth_score + ttl_score) / (max_total*10))


def get_risk_score(ability, willingness):
    return min(ability, willingness)
