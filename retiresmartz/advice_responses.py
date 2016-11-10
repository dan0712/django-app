# -*- coding: utf-8 -*-
from main import constants
from datetime import datetime


# Retiresmartz Advice feed Logic Calls

# On Track / Off Track
def get_on_track(advice):
    return 'If you would like to change any of your retirement details \
you can do so by clicking on the items on this or the previous screen.'


def get_off_track(advice):
    return 'I recommend changing some of your retirement details \
by clicking on this or the previous screen.  This will help you \
to plan to be on track to a better retirement.'


# Change Retirement Age
def get_decrease_retirement_age_to_62(advice):
    # TODO: Need to insert social security benefit in data
    # By increasing your retirement age to 70 your social \
    # security benefit would be estimated to be <estimated SS benefit \
    # multiplied by inflator>
    return "I see you have decreased your retirement age \
to 62. This will reduce your monthly benefit by 25% compared \
to if you retired at 66 giving you an estimated social security \
benefit of {} per month instead of {} if you chose to retire \
at 66. Social security benefits increase by up to 132% the longer \
you work.".format(advice.plan.spendable_income - (advice.plan.spendable_income * .25), advice.plan.spendable_income)


def get_decrease_retirement_age_to_63(advice):
    # TODO: Need to insert social security benefit in data
    #     By increasing your retirement age to 70 \
    # your social security benefit would be estimated to be \
    # <estimated SS benefit multiplied by inflator>
    return "I see you have decreased your retirement age to 63. \
This will reduce your monthly benefit by 20% compared to if \
you retired at 66 giving you an estimated social security \
benefit of {} per month instead of {} if you chose to \
retire at 66. Social security benefits increase by up to 132% \
the longer you work.".format(advice.plan.spendable_income - (advice.plan.spendable_income * .2), advice.plan.spendable_income)


def get_decrease_retirement_age_to_64(advice):
    # TODO: Need to insert social security benefit in data\
    #     By increasing your retirement age to 70 \
    # your social security benefit would be estimated to be \
    # <estimated SS benefit multiplied by inflator>
    return "I see you have decreased your retirement age to 64. \
This will reduce your monthly benefit by 13% compared to \
if you retired at 66 giving you an estimated social security \
benefit of {} per month instead of {} if you chose to \
retire at 66. Social security benefits increase by up to 132% \
the longer you work.".format(advice.plan.spendable_income - (advice.plan.spendable_income * .13), advice.plan.spendable_income)


def get_decrease_retirement_age_to_65(advice):
    # TODO: Need to insert social security benefit in data
    #     By increasing your retirement age to 70 \
    # your social security benefit would be estimated
    # to be <estimated SS benefit multiplied by inflator>
    return "I see you have decreased your retirement age to 65. \
This will reduce your monthly benefit by 7% compared to if \
you retired at 66 giving you an estimated social security \
benefit of <$X> per month instead of <$X> if you chose to \
retire at 66. Social security benefits increase by up to 132% \
the longer you work.".format(advice.plan.spendable_income - (advice.plan.spendable_income * .07), advice.plan.spendable_income)


def get_increase_retirement_age_to_67(advice):
    # TODO: Need to insert social security benefit in data
    return "I see you have increased your retirement age to 67. \
This will increase your monthly benefit by 8% of {} per \
month instead of {} if you chose to retire at 66. Increasing \
your retirement age will adjust the amount of social security \
benefits that you are able to obtain. Social security benefits \
increase by up to 132% the longer you work.".format(advice.plan.spendable_income + (advice.plan.spendable_income * .08), advice.plan.spendable_income)


def get_increase_retirement_age_to_68(advice):
    # TODO: Need to insert social security benefit in data
    return "I see you have increased your retirement age to 68. \
This will increase your monthly benefit by 16% of {} per \
month instead of {} if you chose to retire at 66. Increasing \
your retirement age will adjust the amount of social security \
benefits that you are able to obtain. Social security benefits \
increase by up to 132% the longer you work.".format(advice.plan.spendable_income + (advice.plan.spendable_income * .16), advice.plan.spendable_income)


def get_increase_retirement_age_to_69(advice):
    # TODO: Need to insert social security benefit in data
    return "I see you have increased your retirement age to 69. \
This will increase your monthly benefit by 24% of {} per \
month instead of {} if you chose to retire at 66. Increasing \
your retirement age will adjust the amount of social security \
benefits that you are able to obtain. Social security benefits \
increase by up to 132% the longer you work.".format(advice.plan.spendable_income + (advice.plan.spendable_income * .24), advice.plan.spendable_income)


def get_increase_retirement_age_to_70(advice):
    # TODO: Need to insert social security benefit in data
    return "I see you have increased your retirement age to 70. \
This will increase your monthly benefit by 32% of {} per \
month instead of {} if you chose to retire at 66. Increasing \
your retirement age will adjust the amount of social security \
benefits that you are able to obtain. Social security benefits \
increase by up to 132% the longer you work.".format(advice.plan.spendable_income + (advice.plan.spendable_income * .32), advice.plan.spendable_income)


# Life Expectancy
def get_manually_adjusted_age(advice):
    return 'Your retirement age has been updated. \
Let us know if anything else changes in your wellbeing \
profile by clicking on the life expectancy bubble.'


def get_smoking_yes(advice):
    return 'You could improve your life expectancy score \
by quitting smoking. Do you intend to quit smoking in \
the near future? Yes/No'


def get_quitting_smoking(advice):
    # {formula = (Current Age – 18)/42]*7.7 or 7.3 years}
    formula = ((advice.plan.client.age - 18) / 42) * 7.7
    return "We will add this to your life expectancy. \
Based on your age we will add {} years to your life expectancy.".format(formula)


def get_smoking_no(advice):
    return "By not smoking you're already increasing your \
life expectancy by 7 years."


def get_exercise_only(advice):
    return "Thanks for telling us about your exercise. Exercise \
does impact your life expectancy. Regular exercise for at \
least 20 minutes each day 5 times a week increases your \
life expectancy by up to 3.2 years."


def get_weight_and_height_only(advice):
    return "Thanks for telling us your weight and height. \
These combined details help us better understand your life expectancy."


def get_combination_of_more_than_one_entry_but_not_all(advice):
    return "Thanks for providing more wellbeing information. This helps us \
better understand your life expectancy. By completing all of the \
details we can get an even more accurate understanding."


def get_all_wellbeing_entries(advice):
    return "Thanks for providing your wellbeing information. This gives us \
the big picture and an accurate understanding of your life expectancy."


# Risk Slider
def get_protective_move(advice):
    # TODO: Need to add risk and amounts
    """
    This might reduce the returns from your portfolio or increase \
    the amount you need to contribute from your paycheck each month \
    from <previous amount> to <new amount>
    """
    risk = str(round(advice.plan.recommended_risk, 2))[2:]
    return "I can see you have adjusted your risk profile to be more \
protective. We base your risk profile on the risk questionnaire \
you completed and recommended {}. By adjusting the slider you \
change the asset allocation in your retirement goal.".format(risk)


def get_dynamic_move(advice):
    # TODO: Need to add risk and amounts
    """
    This might increase the returns from your portfolio and decrease the amount \
    you need to contribute from your paycheck each month from <previous amount> \
    to <new amount>
    """
    risk = str(round(advice.plan.recommended_risk, 2))[2:]
    return "I can see you have adjusted your risk profile to be more dynamic. \
We base your risk profile on the risk questionnaire you completed and \
recommended {}. By adjusting the slider you change the asset allocation \
in your retirement goal.\nYou will be taking more risk.".format(risk)


# Contributions / Spending
def get_increase_spending_decrease_contribution(advice):
    # TODO: Need to add $X and $Y calculations, max_contributions needs to come in
    if advice.client.account.account_type == constants.ACCOUNT_TYPE_401K or \
       advice.client.account.account_type == constants.ACCOUNT_TYPE_ROTH401K:
        # [If 401K we need to remember here that for a person under 50 the
        # maximum contribution amount is $18,000 per annum and $24,000
        # if they are over 50]
        if advice.plan.client.age < 50:
            max_contribution = 18000
        else:
            max_contribution = 24000

    rv = "Hey big spender! I can see you want to spend a bit more. \
If you decreased your spending by ${} a week, you could increase your\
retirement income by ${} a week.".format(200, 600)
    if advice.client.employment_status == constants.EMPLOYMENT_STATUS_FULL_TIME or \
       advice.client.employment_status == constants.EMPLOYMENT_STATUS_PART_TIME:
        rv += " Your employer will match these contributions making it easier to reach your goal."

    return rv


def get_increase_contribution_decrease_spending(advice, contrib, income):
    return "Well done, by increasing your retirement contributions to ${} \
a month, you have increased your retirement income by ${} a week.".format(contrib, income)


def get_increase_spending_decrease_contribution(advice, contrib, income):
    # TODO: Need to add $X and $Y calculations
    return "Are you sure you need to increase your spending again and reduce your \
retirement contributions? Just think, if your contributions stayed \
at ${} a month you would be ${} a week better off in retirement.".format(contrib, income)


def get_off_track_item_adjusted_to_on_track(advice):
    years = advice.plan.retirement_age - advice.plan.client.age
    return "Well done, by adjusting your details your retirement goal is now on track.\n\
We want to make sure our advice keeps you on track so that when you retire \
in {} there are no nasty surprises. If you would like to change or see the \
impact of any of your choices you can make changes to your details on \
this dashboard.".format(datetime.now().date().year + years)


def get_on_track_item_adjusted_to_off_track(advice):
    return "Uh oh, you are now off track to achieve your retirement goal. \
We are here to give you’re the advice to ensure you get on track. \
You may want to reconsider the changes you have made to your details \
to get your retirement goal back on track."
