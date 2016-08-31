from django_cron import CronJobBase, Schedule
from portfolios.management.commands.portfolio_calculation_pure import get_all_optimal_portfolios


class CalculatePortfoliosCron(CronJobBase):
    RUN_EVERY_MINUTES = 7*24*60/3  # every 2 days

    schedule = Schedule(run_every_mins=RUN_EVERY_MINUTES)
    code = 'portfolios.cron.calculate_portfolios'   # a unique code

    def do(self):
        pass
        # get_all_optimal_portfolios()

