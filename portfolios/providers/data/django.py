from collections import defaultdict

from django.core.cache import cache
from django.utils import timezone
from portfolios.exceptions import OptimizationException
from main import redis
from main.models import AssetFeatureValue, MarketCap, MarkowitzScale, \
    PortfolioSet, Ticker, InvestmentCycleObservation, InvestmentCyclePrediction
from django_pandas.io import read_frame
from .abstract import DataProviderAbstract


class DataProviderDjango(DataProviderAbstract):

    def get_current_date(self):
        return timezone.now().date()

    def get_fund_price_latest(self, ticker):
        return ticker.daily_prices.order_by('-date')[0].price

    def get_features(self, ticker):
        return ticker.features.values_list('id', flat=True)

    def get_asset_class_to_portfolio_set(self):
        ac_ps = defaultdict(list)
        # Build the asset_class -> portfolio_sets mapping
        for ps in PortfolioSet.objects.all():
            for ac in ps.asset_classes.all():
                ac_ps[ac.id].append(ps.id)
        return ac_ps

    def get_tickers(self):
        """
        Returns a list of all the funds in the system.
        :return:
        """
        return Ticker.objects.all()

    def get_ticker(self, tid):
        return Ticker.objects.get(id=tid)



    def get_market_weight(self, content_type_id, content_object_id):
        mp = MarketCap.objects.filter(instrument_content_type__id=content_type_id,
                                      instrument_object_id=content_object_id).order_by('-date').first()
        return None if mp is None else mp.value

    def get_portfolio_sets_ids(self):
        return PortfolioSet.objects.values_list('id', flat=True)

    def get_asset_feature_values_ids(self):
        return AssetFeatureValue.objects.values_list('id', flat=True)

    def get_goals(self):
        return

    def get_markowitz_scale(self):
        return MarkowitzScale.objects.order_by('-date').first()

    def set_markowitz_scale(self, dt, mn, mx, a, b, c):
        MarkowitzScale.objects.create(date=dt,
                                      min=mn,
                                      max=mx,
                                      a=a,
                                      b=b,
                                      c=c)

    def get_instrument_cache(self):
        key = redis.KEY_INSTRUMENTS(timezone.now().date().isoformat())
        return cache.get(key)

    def set_instrument_cache(self, data):
        key = redis.KEY_INSTRUMENTS(timezone.now().date().isoformat())
        cache.set(key, data, timeout=60 * 60 * 24)

    def get_investment_cycles(self):
        return InvestmentCycleObservation.objects.all().filter(as_of__lt=self.get_current_date()).order_by('as_of')

    def get_last_cycle_start(self, investment_cycles):
        obs = investment_cycles
        # Populate the cache as we'll be hitting it a few times. Boolean evaluation causes full cache population
        if not obs:
            raise OptimizationException("There are no historic observations available")

        # Get the investment cycle for the current date
        current_cycle = obs.last().cycle

        # Get the end date of the last non-current cycle before the current one
        pre_dt = obs.exclude(cycle=current_cycle).last().as_of

        # Get the end date of the previous time the current cycle was
        pre_on_dt = obs.filter(as_of__lt=pre_dt).filter(cycle=current_cycle).last().as_of

        # Get the end date of the time before that when we were not in the current cycle
        pre_off_dt = obs.filter(as_of__lt=pre_on_dt).exclude(cycle=current_cycle).last().as_of

        # Not get the first date after this when the current cycle was on and we have the answer
        return obs.filter(as_of__gt=pre_off_dt).first().as_of

    def get_cycle_obs(self, begin_date):
        qs = self.get_investment_cycles().filter(as_of__gt=begin_date)
        return read_frame(qs, fieldnames=['cycle'], index_col='as_of', verbose=False)['cycle']

    def get_investment_cycle_predictions(self):
        return InvestmentCyclePrediction.objects.all().filter(as_of__lt=self.get_current_date()).order_by('as_of')

    def get_probs_df(self, begin_date):
        qs = self.get_investment_cycle_predictions().filter(as_of__gt=begin_date)
        probs_df = read_frame(qs,
                              fieldnames=['eq', 'eq_pk', 'pk_eq', 'eq_pit', 'pit_eq'],
                              index_col='as_of')
        return probs_df
