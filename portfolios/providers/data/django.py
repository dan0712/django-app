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
        latest_ticker = ticker.daily_prices.order_by('-date').first()
        if latest_ticker:
            return latest_ticker.price
        return None

    def get_instrument_daily_prices(self, ticker):
        return ticker.daily_prices.order_by('-date')

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
        return cache.get(redis.Keys.INSTRUMENT_DATA)

    def set_instrument_cache(self, data):
        cache.set(redis.Keys.INSTRUMENT_DATA, data, timeout=60 * 60 * 24)

    def get_investment_cycles(self):
        # Populate the cache as we'll be hitting it a few times. Boolean evaluation causes full cache population
        obs = InvestmentCycleObservation.objects.all().filter(as_of__lt=self.get_current_date()).order_by('as_of')
        if not obs:
            raise OptimizationException("There are no historic observations available")
        return obs

    def get_last_cycle_start(self):
        obs = self.get_investment_cycles()

        current_cycle = obs.last().cycle

        # Get the end date and value of the last non-current full cycle before the current one
        pre_dt = obs.exclude(cycle=current_cycle).last().as_of
        previous_cycle = obs.filter(as_of=pre_dt).last().cycle

        # Get the end date of the cycle before the previous full cycle
        if current_cycle == InvestmentCycleObservation.Cycle.EQ.value:
            pre_dt_start = obs.filter(as_of__lte=pre_dt).exclude(cycle=previous_cycle).last().as_of
            pre_on_dt = obs.filter(as_of__lt=pre_dt_start).filter(cycle=previous_cycle).last().as_of
        else:
            pre_dt_start = obs.filter(as_of__lt=pre_dt).filter(cycle=current_cycle).last().as_of
            pre_on_dt = obs.filter(as_of__lt=pre_dt_start).exclude(cycle=current_cycle).last().as_of

        # Now get the first date after this when the full previous cycle was on
        return obs.filter(as_of__gt=pre_on_dt).first().as_of

    def get_cycle_obs(self, begin_date):
        qs = self.get_investment_cycles().filter(as_of__gte=begin_date)
        return read_frame(qs, fieldnames=['cycle'], index_col='as_of', verbose=False)['cycle']

    def get_investment_cycle_predictions(self):
        return InvestmentCyclePrediction.objects.all().filter(as_of__lt=self.get_current_date()).order_by('as_of')

    def get_probs_df(self, begin_date):
        qs = self.get_investment_cycle_predictions().filter(as_of__gt=begin_date)
        probs_df = read_frame(qs,
                              fieldnames=['eq', 'eq_pk', 'pk_eq', 'eq_pit', 'pit_eq'],
                              index_col='as_of')
        return probs_df
