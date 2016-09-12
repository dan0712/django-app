from django.core.cache import cache

from main import redis
from main.models import AssetFeatureValue, MarketCap, MarkowitzScale, \
    PortfolioSet, Ticker
from portfolios.calculation import *
from portfolios.management.commands.providers.instruments_data_providers.data_provider_abstract import DataProviderAbstract


class DataProviderDjango(DataProviderAbstract):
    def __init__(self):
        pass

    def move_date_forward(self):
        # this function is only used in backtesting
        pass

    def get_current_date(self):
        return datetime.today()

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

    def get_ticker(self, id):
        return Ticker.objects.get(id=id)

    def get_market_weight(self, content_type_id, content_object_id):
        mp = MarketCap.objects.filter(instrument_content_type__id=content_type_id,
                                      instrument_object_id=content_object_id).order_by('-date').first()
        return None if mp is None else mp.value

    def get_portfolio_sets_ids(self):
        return PortfolioSet.objects.values_list('id', flat=True)

    def get_asset_feature_values_ids(self):
        return AssetFeatureValue.objects.values_list('id', flat=True)

    def get_masks(self, instruments, fund_mask_name, portfolio_set_mask_prefix):
        masks = pd.DataFrame(False, index=instruments.index, columns=self.get_asset_feature_values_ids())
        masks[fund_mask_name] = instruments['bid'].notnull()

        psid_miloc = {}
        portfolio_sets_ids = self.get_portfolio_sets_ids()
        for psid in portfolio_sets_ids:
            mid = portfolio_set_mask_prefix + str(psid)
            masks[mid] = False
            psid_miloc[psid] = masks.columns.get_loc(mid)

        # Add the feature masks
        for ix, row in enumerate(instruments.itertuples()):
            for fid in row[5]:
                masks.iloc[ix, masks.columns.get_loc(fid)] = True
            for psid in row[6]:
                masks.iloc[ix, psid_miloc[psid]] = True
        return masks

    def get_goals(self):
        return

    def get_markowitz_scale(self):
        return MarkowitzScale.objects.order_by('-date').first()

    def set_markowitz_scale(self, date, min, max, a, b ,c):
        MarkowitzScale.objects.create(date=date,
                                      min=min,
                                      max=max,
                                      a=a,
                                      b=b,
                                      c=c)

    def get_instruments(self):
        key = redis.KEY_INSTRUMENTS(datetime.today().isoformat())
        data = cache.get(key)

        if data is None:
            data = build_instruments(data_provider=self)
            cache.set(key, data, timeout=60 * 60 * 24)
        return data

    def set_cache(self, *args):
        pass





