from django_cron import CronJobBase, Schedule
from portfolios.management.commands.calculate_portfolios import calculate_portfolios


class CalculatePortfoliosCron(CronJobBase):
    RUN_EVERY_MINS = 7*24*60 # every week

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'portfolios.cron.calculate_portfolios'   # a unique code

    def do(self):
        calculate_portfolios()
        pass