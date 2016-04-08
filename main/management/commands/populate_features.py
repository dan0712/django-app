from django.core.management.base import BaseCommand

from main.models import AssetFeature, AssetFeatureValue, Ticker

# TODO: Remove this file once the admin UI is updated to use the new asset features.

region_feature = AssetFeature.Standard.REGION.get_object()
ac_feature = AssetFeature.Standard.ASSET_CLASS.get_object()
curr_feature = AssetFeature.Standard.CURRENCY.get_object()

stock_type_feature_value = AssetFeatureValue.Standard.ASSET_TYPE_STOCK.get_object()
bond_type_feature_value = AssetFeatureValue.Standard.ASSET_TYPE_BOND.get_object()
satellite_feature_value = AssetFeatureValue.Standard.FUND_TYPE_SATELLITE.get_object()
core_feature_value = AssetFeatureValue.Standard.FUND_TYPE_CORE.get_object()
eth_feature_value = AssetFeatureValue.Standard.SRI_OTHER.get_object()


def get_region_feature(name):
    if name == 'AU':
        return AssetFeatureValue.Standard.REGION_AUSTRALIAN.get_object()
    if name == 'EU':
        return AssetFeatureValue.objects.get_or_create(name='European', feature=region_feature)[0]
    if name == 'US':
        return AssetFeatureValue.objects.get_or_create(name='American (US)', feature=region_feature)[0]
    if name == 'CN':
        return AssetFeatureValue.objects.get_or_create(name='Chinese', feature=region_feature)[0]
    if name == 'INT':
        return AssetFeatureValue.objects.get_or_create(name='International', feature=region_feature)[0]
    if name == 'AS':
        return AssetFeatureValue.objects.get_or_create(name='Asian', feature=region_feature)[0]
    if name == 'JAPAN':
        return AssetFeatureValue.objects.get_or_create(name='Japanese', feature=region_feature)[0]
    if name == 'UK':
        return AssetFeatureValue.objects.get_or_create(name='UK', feature=region_feature)[0]
    if name == 'EM':
        return AssetFeatureValue.objects.get_or_create(name='Emerging Markets', feature=region_feature)[0]
    raise Exception("Unknown region")


def populate_features():
    """
    Converts the old constraint version to the new, and saves them in the db.
    :return: Nothing
    """

    # Populate the features for instruments from old features #
    for ticker in Ticker.objects.all():
        r_feat = get_region_feature(ticker.region.name)
        ac_feat = AssetFeatureValue.objects.get_or_create(name=ticker.asset_class.display_name, feature=ac_feature)[0]
        curr_feat = AssetFeatureValue.objects.get_or_create(name=ticker.currency, feature=curr_feature)[0]
        at_feat = stock_type_feature_value if ticker.asset_class.investment_type == "STOCKS" else bond_type_feature_value
        ticker.features.clear()
        ticker.features.add(r_feat, ac_feat, curr_feat, at_feat)
        if ticker.ethical:
            ticker.features.add(eth_feature_value)
        ticker.features.add(core_feature_value if ticker.etf else satellite_feature_value)


class Command(BaseCommand):
    help = 'Populate asset features for all assets in the system.'

    def handle(self, *args, **options):
        populate_features()
