from datetime import date
from functools import lru_cache

from retiresmartz.utils.ss_calculator import get_retire_data


@lru_cache()
def calculate_payments(dob: date, income: int):
    """
    Calculates the pension payments for retirement ages 62-70
    :param dob: THe date of birth of the person
    :param income: The current annual income.
    :return: a dict {age: amount} for each applicable age
    """
    ssa_params = {
        'dobmon': dob.month,
        'dobday': dob.day,
        'yob': dob.year,
        'earnings': income,
        'lastYearEarn': '',  # not using
        'lastEarn': '',  # not using
        'retiremonth': '',  # only using for past-FRA users
        'retireyear': '',  # only using for past-FRA users
        'dollars': 1,  # (1) benefits to be calculated in current-year dollars. (0) = Future dollars
        'prgf': 2,  # Past relative growth factor (How much in comparison to national average have your wages grown in past)
    }
    data = get_retire_data(ssa_params, 'en')
    return {int(agestr.split()[1]): amt for agestr, amt in data['data']['benefits'].items()}

