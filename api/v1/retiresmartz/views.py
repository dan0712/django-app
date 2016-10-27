from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin
from api.v1.views import ApiViewMixin
from retiresmartz.models import RetirementPlan, RetirementAdvice
from main.models import Ticker
from client.models import Client
from support.models import SupportRequest
from django.db.models import Q
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from . import serializers
import logging
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
            return Response(
            {'error': 'Unable to update a RetirementPlan that has been agreed on'},
            status=status.HTTP_400_BAD_REQUEST)
        return super(RetiresmartzViewSet, self).update(request, *args, **kwargs)

    @detail_route(methods=['get'], url_path='suggested-retirement-income')
    def suggested_retirement_income(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates a suggested retirement income based on the client's retirement plan and personal profile.
        """
        # TODO: Make this work
        return Response(1234)

    @detail_route(methods=['get'], url_path='calculate-contributions')
    def calculate_contributions(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates suggested contributions (value for the amount in the btc and atc) that will generate the desired
        retirement income.
        """
        # TODO: Make this work
        return Response({'btc_amount': 1111, 'atc_amount': 0})

    @list_route(methods=['post'], url_path='calculate-income')
    def calculate_income(self, request, parent_lookup_client, format=None):
        """
        Calculates retirement income possible given the current contributions and other details on the retirement plan.
        """
        # TODO: Make this work
        return Response(2345)

    @detail_route(methods=['get'], url_path='calculate-balance-income')
    def calculate_balance_income(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the retirement balance required to provide the desired_income as specified in the plan.
        """
        # TODO: Make this work
        return Response(5555555)

    @detail_route(methods=['get'], url_path='calculate-income-balance')
    def calculate_income_balance(self, request, parent_lookup_client, pk, format=None):
        """
        Calculates the retirement income possible with a supplied retirement balance and other details on the
        retirement plan.
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
        Calculates the contributions required to generate the given retirement balance.
        """
        # TODO: Make this work
        return Response({'btc_amount': 2222, 'atc_amount': 88})

    @list_route(methods=['post'], url_path='calculate')
    def calculate(self, request, parent_lookup_client, format=None):
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
        # try:
        #     retirement_plan = RetirementPlan.objects.get(pk=pk)
        # except:
        #     return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            client = Client.objects.get(pk=parent_lookup_client)
        except:
            return Response({'error': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.RetirementPlanCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        now = timezone.now()
        first_year = client.date_of_birth.year + serializer.validated_data['retirement_age']
        last_year = client.date_of_birth.year + serializer.validated_data['selected_life_expectancy']
        day_interval = ((last_year - first_year) * 365) / 50
        income_start = 20000
        assets_start = 100000
        for i in range(1, 50):
            income = income_start + (i * 50)
            assets = assets_start + (i * 1000)
            dt = now + relativedelta(days=i * day_interval)
            projection.append([income, assets, dt])
        return Response({'portfolio': portfolio, 'projection': projection})


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
