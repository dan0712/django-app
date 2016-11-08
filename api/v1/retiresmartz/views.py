import logging
from datetime import date

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin

import scipy.stats as st

from api.v1.goals.serializers import PortfolioSerializer
from api.v1.views import ApiViewMixin
from common.utils import d2ed
from portfolios.calculation import Unsatisfiable
from retiresmartz.calculator import create_settings, Calculator
from retiresmartz.calculator.assets import TaxDeferredAccount
from retiresmartz.calculator.cashflows import ReverseMortgage, InflatedCashFlow, EmploymentIncome
from retiresmartz.calculator.desired_cashflows import RetiresmartzDesiredCashFlow
from retiresmartz.calculator.social_security import calculate_payments
from retiresmartz.models import RetirementPlan, RetirementAdvice
from retiresmartz import advice_responses
from client.models import Client
from main.models import Ticker
from main.event import Event
from support.models import SupportRequest
from . import serializers
logger = logging.getLogger('api.v1.retiresmartz.views')


class RetiresmartzViewSet(ApiViewMixin, NestedViewSetMixin, ModelViewSet):
    model = RetirementPlan
    permission_classes = (IsAuthenticated,)

    # We don't want pagination for this viewset. Remove this line to enable.
    pagination_class = None

    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = RetirementPlan.objects.all()

    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_class = serializers.RetirementPlanSerializer
    serializer_response_class = serializers.RetirementPlanSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RetirementPlanSerializer
        elif self.request.method == 'POST':
            return serializers.RetirementPlanWritableSerializer
        elif self.request.method == 'PUT':
            return serializers.RetirementPlanWritableSerializer

    def get_queryset(self):
        """
        The nested viewset takes care of only returning results for the client we are looking at.
        We need to add logic to only allow access to users that can view the plan.
        """
        qs = super(RetiresmartzViewSet, self).get_queryset()
        # Check user object permissions
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)

    def perform_create(self, serializer):
        """
        We don't allow users to create retirement plans for others... So we set the client from the URL and validate
        the user has access to it.
        :param serializer:
        :return:
        """
        user = SupportRequest.target_user(self.request)
        client = Client.objects.filter_by_user(user).get(id=int(self.get_parents_query_dict()['client']))
        return serializer.save(client=client)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.agreed_on:
            return Response({'error': 'Unable to update a RetirementPlan that has been agreed on'},
                            status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        orig = RetirementPlan.objects.get(pk=instance.pk)
        updated = serializer.update(instance, serializer.validated_data)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # refresh the instance from the database.
            instance = self.get_object()
            serializer = self.get_serializer(instance)

        # RetirementAdvice Triggers

        # Spending and Contributions
        if orig.btc > updated.btc:
            logger.error('%s %s' % (orig.btc, updated.btc))
            # spending increased, contributions decreased
            e = Event.RETIRESMARTZ_SPENDABLE_INCOME_UP_CONTRIB_DOWN.log(None,
                                                                        orig.btc,
                                                                        updated.btc,
                                                                        user=updated.client.user,
                                                                        obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_decrease_spending_increase_contribution(advice)
            advice.save()

        if orig.btc < updated.btc:
            logger.error('%s %s' % (orig.btc, updated.btc))
            e = Event.RETIRESMARTZ_CONTRIB_UP_SPENDING_DOWN.log(None,
                                                                orig.btc,
                                                                updated.btc,
                                                                user=updated.client.user,
                                                                obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_increase_contribution_decrease_spending(advice)
            advice.save()

            # contributions increased, spending decreased
            e = Event.RETIRESMARTZ_SPENDABLE_INCOME_DOWN_CONTRIB_UP.log(None,
                                                                        orig.btc,
                                                                        updated.btc,
                                                                        user=updated.client.user,
                                                                        obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_decrease_spending_increase_contribution(advice)
            advice.save()

        # Risk Slider Changed
        if updated.desired_risk < orig.desired_risk and \
           updated.desired_risk < updated.recommended_risk:
            # protective move
            e = Event.RETIRESMARTZ_PROTECTIVE_MOVE.log(None,
                                                       orig.desired_risk,
                                                       updated.desired_risk,
                                                       user=updated.client.user,
                                                       obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_protective_move(advice)
            advice.save()
        elif updated.desired_risk > orig.desired_risk and updated.desired_risk > orig.recommended_risk:
            # dynamic move
            e = Event.RETIRESMARTZ_DYNAMIC_MOVE.log(None,
                                                    orig.desired_risk,
                                                    updated.desired_risk,
                                                    user=updated.client.user,
                                                    obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_dynamic_move(advice)
            advice.save()

        # age manually adjusted
        if updated.retirement_age != orig.retirement_age:
            e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                               orig.retirement_age,
                                                               updated.retirement_age,
                                                               user=updated.client.user,
                                                               obj=updated)
            advice = RetirementAdvice(plan=updated, trigger=e)
            advice.text = advice_responses.get_manually_adjusted_age(advice)
            advice.save()

        # Retirement Age Adjusted
        if updated.retirement_age >= 62 and updated.retirement_age <= 70:
            if orig.retirement_age != updated.retirement_age:
                # retirement age changed
                if orig.retirement_age > 62 and updated.retirement_age == 62:
                    # decreased to age 62
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_decrease_retirement_age_to_62(advice)
                    advice.save()
                elif orig.retirement_age > 63 and updated.retirement_age == 63:
                    # decreased to age 63
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_decrease_retirement_age_to_63(advice)
                    advice.save()
                elif orig.retirement_age > 64 and updated.retirement_age == 64:
                    # decreased to age 64
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_decrease_retirement_age_to_64(advice)
                    advice.save()
                elif orig.retirement_age > 65 and updated.retirement_age == 65:
                    # decreased to age 65
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_decrease_retirement_age_to_65(advice)
                    advice.save()
                elif orig.retirement_age < 67 and updated.retirement_age == 67:
                    # increased to age 67
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_increase_retirement_age_to_67(advice)
                    advice.save()
                elif orig.retirement_age < 68 and updated.retirement_age == 68:
                    # increased to age 68
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_increase_retirement_age_to_68(advice)
                    advice.save()
                elif orig.retirement_age < 69 and updated.retirement_age == 69:
                    # increased to age 69
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_increase_retirement_age_to_69(advice)
                    advice.save()
                elif orig.retirement_age < 70 and updated.retirement_age == 70:
                    # increased to age 70
                    e = Event.RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED.log(None,
                                                                       orig.retirement_age,
                                                                       updated.retirement_age,
                                                                       user=updated.client.user,
                                                                       obj=updated)
                    advice = RetirementAdvice(plan=updated, trigger=e)
                    advice.text = advice_responses.get_increase_retirement_age_to_70(advice)
                    advice.save()

        if orig.on_track != updated.on_track:
            # user update to goal caused on_track status changed
            if updated.on_track:
                # RetirementPlan now on track
                e = Event.RETIRESMARTZ_ON_TRACK_NOW.log(None,
                                                        user=updated.client.user,
                                                        obj=updated)
                advice = RetirementAdvice(plan=updated, trigger=e)
                advice.text = advice_responses.get_off_track_item_adjusted_to_on_track(advice)
                advice.save()
            else:
                # RetirementPlan now off track
                e = Event.RETIRESMARTZ_OFF_TRACK_NOW.log(None,
                                                         user=updated.client.user,
                                                         obj=updated)
                advice = RetirementAdvice(plan=updated, trigger=e)
                advice.text = advice_responses.get_on_track_item_adjusted_to_off_track(advice)
                advice.save()

        return Response(self.serializer_response_class(updated).data)

    @detail_route(methods=['get'], url_path='suggested-retirement-income')
    def suggested_retirement_income(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates a suggested retirement income based on the client's
        retirement plan and personal profile.
        """
        # TODO: Make this work
        return Response(1234)

    @detail_route(methods=['get'], url_path='calculate-contributions')
    def calculate_contributions(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates suggested contributions (value for the amount in the
        btc and atc) that will generate the desired retirement income.
        """
        # TODO: Make this work
        return Response({'btc_amount': 1111, 'atc_amount': 0})

    @detail_route(methods=['get'], url_path='calculate-income')
    def calculate_income(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates retirement income possible given the current contributions
        and other details on the retirement plan.
        """
        # TODO: Make this work
        return Response(2345)

    @detail_route(methods=['get'], url_path='calculate-balance-income')
    def calculate_balance_income(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the retirement balance required to provide the
        desired_income as specified in the plan.
        """
        # TODO: Make this work
        return Response(5555555)

    @detail_route(methods=['get'], url_path='calculate-income-balance')
    def calculate_income_balance(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the retirement income possible with a supplied
        retirement balance and other details on the retirement plan.
        """
        # TODO: Make this work
        return Response(1357)

    @detail_route(methods=['get'], url_path='calculate-balance-contributions')
    def calculate_balance_contributions(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the retirement balance generated from the contributions.
        """
        # TODO: Make this work
        return Response(6666666)

    @detail_route(methods=['get'], url_path='calculate-contributions-balance')
    def calculate_contributions_balance(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the contributions required to generate the
        given retirement balance.
        """
        # TODO: Make this work
        return Response({'btc_amount': 2222, 'atc_amount': 88})

    @detail_route(methods=['get'], url_path='calculate-demo')
    def calculate_demo(self, request, parent_lookup_client, pk, format=None):
        """
        Calculate the single projection values for the
        current retirement plan settings.
        {
          "portfolio": [
            # list of [fund id, weight as percent]. There will be max 33 of these. Likely 5-10
            [1, 5],
            [53, 12],
            ...
          ],
          "projection": [
            # this is the asset and cash-flow projection. It is a list of [date, assets, income]. There will be at most 50 of these. (21 bytes each)
            [143356, 120000, 2000],
            [143456, 119000, 2004],
            ...
          ]
        }
        "portfolio": 10% each for the first 10 tickers in the systems
        that aren't Closed.
        "projection": 50 time points evenly spaced along the
        remaining time until expected end of life.  Each time
        point with assets starting at 100000,
        going up by 1000 every point, income starting
        at 200000, increasing by 50 every point.
        """
        retirement_plan = self.get_object()
        tickers = Ticker.objects.filter(~Q(state=Ticker.State.CLOSED.value))
        portfolio = []
        projection = []
        for idx, ticker in enumerate(tickers[:10]):
            percent = 0
            if idx <= 9:
                # 10% each for first 10 tickers
                percent = 10
            portfolio.append([ticker.id, percent])
        # grab 50 evenly spaced time points between dob and current time
        today = timezone.now().date()
        last_day = retirement_plan.client.date_of_birth + relativedelta(years=retirement_plan.selected_life_expectancy)
        day_interval = (last_day - today) / 49
        income_start = 20000
        assets_start = 100000
        for i in range(50):
            income = income_start + (i * 50)
            assets = assets_start + (i * 1000)
            dt = today + i * day_interval
            projection.append([d2ed(dt), assets, income])
        return Response({'portfolio': portfolio, 'projection': projection})

    @detail_route(methods=['get'], url_path='calculate')
    def calculate(self, request, parent_lookup_client, pk, format=None):
        """
        Calculate the single projection values for the current retirement plan.
        {
          "portfolio": [
            # list of [fund id, weight as percent]. There will be max 20 of these. Likely 5-10
            [1, 5],
            [53, 12],
            ...
          ],
          "projection": [
            # this is the asset and cash-flow projection. It is a list of [date, assets, income]. There will be at most 50 of these. (21 bytes each)
            [43356, 120000, 2000],
            [43456, 119000, 2004],
            ...
          ]
        }
        """
        plan = self.get_object()

        # We need a date of birth for the client
        if not plan.client.date_of_birth:
            raise ValidationError("Client must have a date of birth entered to calculate retirement plans.")

        # TODO: We can cache the portfolio on the plan and only update it every 24hrs, or if the risk changes.
        try:
            settings = create_settings(plan)
        except Unsatisfiable as e:
            rdata = {'reason': "No portfolio could be found: {}".format(e)}
            if e.req_funds is not None:
                rdata['req_funds'] = e.req_funds
            return Response({'error': rdata}, status=status.HTTP_400_BAD_REQUEST)

        plan.set_settings(settings)
        plan.save()

        # Get the z-multiplier for the given confidence
        z_mult = -st.norm.ppf(plan.expected_return_confidence)
        performance = settings.portfolio.er + z_mult * settings.portfolio.stdev

        today = timezone.now().date()
        retire_date = max(today, plan.client.date_of_birth + relativedelta(years=plan.retirement_age))
        death_date = max(retire_date, plan.client.date_of_birth + relativedelta(years=plan.selected_life_expectancy))

        # Pre-retirement income cash flow
        income_calc = EmploymentIncome(income=plan.income / 12,
                                       growth=0.01,
                                       today=today,
                                       end_date=retire_date)

        ss_all = calculate_payments(plan.client.date_of_birth, plan.income)
        ss_income = ss_all.get(plan.retirement_age, None)
        if ss_income is None:
            ss_income = sorted(ss_all)[0]
        ss_payments = InflatedCashFlow(ss_income, today, retire_date, death_date)

        cash_flows = [ss_payments]

        # TODO: Call the logic that determines the retirement accounts to figure out what accounts to use.
        # TODO: Get the tax rate to use when withdrawing from the account at retirement
        # For now we assume we want a tax deferred 401K
        acc_401k = TaxDeferredAccount(dob=plan.client.date_of_birth,
                                      tax_rate=0.0,
                                      name='401k',
                                      today=today,
                                      opening_balance=plan.opening_tax_deferred_balance,
                                      growth=performance,
                                      retirement_date=retire_date,
                                      end_date=death_date,
                                      contributions=plan.btc / 12)

        assets = [acc_401k]

        if plan.reverse_mortgage and plan.retirement_home_price is not None:
            cash_flows.append(ReverseMortgage(home_value=plan.retirement_home_price,
                                              value_date=today,
                                              start_date=retire_date,
                                              end_date=death_date))

        if plan.paid_days > 0:
            # Average retirement income is 116 per day as of September 2016, working until age 80
            cash_flows.append(InflatedCashFlow(amount=116*plan.paid_days,
                                               today=date(2016, 9, 1),
                                               start_date=retire_date,
                                               end_date=plan.client.date_of_birth + relativedelta(years=80)))

        # The desired cash flow generator.
        rdcf = RetiresmartzDesiredCashFlow(current_income=income_calc,
                                           retirement_income=plan.desired_income / 12,
                                           today=today,
                                           retirement_date=retire_date,
                                           end_date=death_date)
        # Add the income cash flow to the list of cash flows.
        cash_flows.append(rdcf)

        calculator = Calculator(cash_flows=cash_flows, assets=assets)

        asset_values, income_values = calculator.calculate(rdcf)

        # Convert these returned values to a format for the API
        catd = pd.concat([asset_values.sum(axis=1), income_values['actual']], axis=1)
        locs = np.linspace(0, len(catd)-1, num=50, dtype=int)
        proj_data = [(d2ed(d), a, i) for d, a, i in catd.iloc[locs, :].itertuples()]

        pser = PortfolioSerializer(instance=settings.portfolio)

        return Response({'portfolio': pser.data, 'projection': proj_data})


class RetiresmartzAdviceViewSet(ApiViewMixin, NestedViewSetMixin, ModelViewSet):
    model = RetirementPlan
    permission_classes = (IsAuthenticated,)
    queryset = RetirementAdvice.objects.filter(read=None)  # unread advice
    serializer_class = serializers.RetirementAdviceReadSerializer
    serializer_response_class = serializers.RetirementAdviceReadSerializer

    def get_queryset(self):
        """
        The nested viewset takes care of only returning results for the client we are looking at.
        We need to add logic to only allow access to users that can view the plan.
        """
        qs = super(RetiresmartzAdviceViewSet, self).get_queryset()
        # Check user object permissions
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.RetirementAdviceReadSerializer
        elif self.request.method == 'PUT':
            return serializers.RetirementAdviceWritableSerializer
