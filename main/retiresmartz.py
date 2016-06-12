
class Calculator(object):
    """
    The retirement calculator allows calculation of various aspects of retirement.
    """
    def __init__(self, plan):
        """
        Initialise the calculator
        :param plan: The retirement plan we are calculating against.
        """
        self._plan = plan

    def balance_from_income(self, inc: int):
        """
        Calculates the retirement balance required given a desired retirement income.
        Calculations are compounded in accordance with the calculator's compounding period.
        :param inc: The desired retirement income in today's dollars.
        :return: int required balance at retirement.
        """
        return 0

    def income_from_balance(self, bal: int) -> int:
        """
        Calculates the income during retirement possible given a retirement balance
        Calculations are compounded in accordance with the calculator's compounding period.
        :param bal: The account balance at retirement
        :return: The income possible during retirement in today's dollars
        """
        return 0

    def contributions_from_balance(self, bal: int) -> (int, int):
        """
        Calculates the required contributions given a desired balance at retirement.
        Returns are compounded in accordance with the calculator's compounding period.
        :param bal: The desired balance at retirement.
        :return: A tuple (btc, atc) where btc and atc are the before and after tax contributions into the retirement
        account required to generate the given balance.
        """
        return (0, 0)

    def balance_from_contributions(self, btc: int, atc: int) -> int:
        """
        Calculates the balance at retirement generated from the given before and after tax contributions.
        Returns are compounded in accordance with the calculator's compounding period.
        :param btc: Before tax contributions into the retirement account
        :param atc: After tax contributions into the retirement account
        :return: The generated balance given the contributions
        """
        return 0

    def period_opening_balance(self, sd, ed, cb) -> int:
        """
        Returns the balance required at the start date to generate the given closing balance at the end date.
        :param sd: The start date for the period
        :param ed: The end date for the period
        :param cb: The closing balance for the period.
        :return: The opening balance for the period.
        """
        return 0

    def period_closing_balance(self, sd, ed, ob) -> int:
        """
        Returns the balance generated at the end date given an opening balance and time period.
        :param sd: The start date for the period
        :param ed: The end date for the period
        :param ob: The opening balance for the period.
        :return: The closing balance for the period.
        """
        return 0