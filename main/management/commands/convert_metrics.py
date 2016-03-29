import ujson

from django.core.management.base import BaseCommand

from main.models import GoalMetric, Goal, AssetFeature, AssetFeatureValue, Ticker, Region

# TODO: Remove this file once the UI is updated to use the new constraints.

region_feature = AssetFeature.objects.get_or_create(name='Region')[0]
at_feature = AssetFeature.objects.get_or_create(name='Asset Type')[0]
stock_type_feature_value = AssetFeatureValue.objects.get_or_create(name='Stocks Only',
                                                                   defaults={'feature': at_feature})[0]
bond_type_feature_value = AssetFeatureValue.objects.get_or_create(name='Bonds Only',
                                                                  defaults={'feature': at_feature})[0]
fund_type_feature = AssetFeature.objects.get_or_create(name='Fund Type')[0]
satellite_feature_value = AssetFeatureValue.objects.get_or_create(name='Satellite',
                                                                  defaults={'feature': fund_type_feature})[0]
core_feature_value = AssetFeatureValue.objects.get_or_create(name='Core',
                                                                  defaults={'feature': fund_type_feature})[0]

sr_feature = AssetFeature.objects.get_or_create(name='Social Responsibility')[0]
eth_feature_value = AssetFeatureValue.objects.get_or_create(name='Ethical', defaults={'feature': sr_feature})[0]
ac_feature = AssetFeature.objects.get_or_create(name='Asset Class')[0]
curr_feature = AssetFeature.objects.get_or_create(name='Currency')[0]


def get_region_feature(name):
    if name == 'AU':
        return AssetFeatureValue.objects.get_or_create(name='Australian', defaults={'feature': region_feature})[0]
    if name == 'EU':
        return AssetFeatureValue.objects.get_or_create(name='European', defaults={'feature': region_feature})[0]
    if name == 'US':
        return AssetFeatureValue.objects.get_or_create(name='American (US)', defaults={'feature': region_feature})[0]
    if name == 'CN':
        return AssetFeatureValue.objects.get_or_create(name='Chinese', defaults={'feature': region_feature})[0]
    if name == 'INT':
        return AssetFeatureValue.objects.get_or_create(name='International', defaults={'feature': region_feature})[0]
    if name == 'AS':
        return AssetFeatureValue.objects.get_or_create(name='Asian', defaults={'feature': region_feature})[0]
    if name == 'JAPAN':
        return AssetFeatureValue.objects.get_or_create(name='Japanese', defaults={'feature': region_feature})[0]
    if name == 'UK':
        return AssetFeatureValue.objects.get_or_create(name='UK', defaults={'feature': region_feature})[0]
    if name == 'EM':
        return AssetFeatureValue.objects.get_or_create(name='Emerging Markets', defaults={'feature': region_feature})[0]
    raise Exception("Unknown region")


def convert_goal(goal):
    metrics = []
    not_incl = {region.name: get_region_feature(region.name) for region in Region.objects.all()}

    if goal.optimization_mode == 1:
        # TODO: This json should go. We should simply get the region (min,max) percentage constraints from the model
        for region in ujson.loads(goal.picked_regions):
            del not_incl[region]
    else:
        assert goal.optimization_mode == 2
        for region, sz in goal.region_sizes.items():
            metrics.append(GoalMetric(goal=goal,
                                      type=0,
                                      feature=not_incl[region],
                                      comparison=1,
                                      rebalance_type=1,
                                      rebalance_thr=0.05,
                                      configured_val=sz))
            del not_incl[region]

    for fid in not_incl.values():
        metrics.append(GoalMetric(goal=goal,
                   type=0,
                   feature=fid,
                   comparison=1,
                   rebalance_type=1,
                   rebalance_thr=0.0,
                   configured_val=0.0))

    # Default set the risk slider to medium
    metrics.append(GoalMetric(goal=goal,
               type=1,
               comparison=1,
               rebalance_type=1,
               rebalance_thr=0.05,
               configured_val=0.5))

    metrics.append(GoalMetric(goal=goal,
                              type=0,
                              feature=stock_type_feature_value,
                              comparison=1,
                              rebalance_type=1,
                              rebalance_thr=0.05,
                              configured_val=goal.allocation))

    metrics.append(GoalMetric(goal=goal,
                              type=0,
                              feature=satellite_feature_value,
                              comparison=1,
                              rebalance_type=1,
                              rebalance_thr=0.05,
                              configured_val=goal.satellite_pct))
    GoalMetric.objects.filter(goal=goal).delete()
    GoalMetric.objects.bulk_create(metrics)

def convert_constraints():
    """
    Converts the old constraint version to the new, and saves them in the db.
    :param goal:
    :return: Nothing
    """

    ## Populate the features for instruments from old features ##
    for ticker in Ticker.objects.all():
        r_feat = get_region_feature(ticker.region.name)
        ac_feat = AssetFeatureValue.objects.get_or_create(name=ticker.asset_class.name, defaults={'feature': ac_feature})[0]
        curr_feat = AssetFeatureValue.objects.get_or_create(name=ticker.currency, defaults={'feature': curr_feature})[0]
        at_feat = stock_type_feature_value if ticker.asset_class.investment_type == "STOCKS" else bond_type_feature_value
        ticker.features.clear()
        ticker.features.add(r_feat, ac_feat, curr_feat, at_feat)
        if ticker.ethical:
            ticker.features.add(eth_feature_value)
        ticker.features.add(core_feature_value if ticker.etf else satellite_feature_value)

    ## POPULATE the metrics for goals ##
    #for goal in Goal.objects.all():
    #    convert_goal(goal)


class Command(BaseCommand):
    help = 'Calculate all the optimal portfolios for all the goals in the system.'

    def handle(self, *args, **options):
        convert_constraints()
