from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.views import ApiViewMixin
from retiresmartz.models import RetirementPlan
from client.models import Client
from support.models import SupportRequest

from . import serializers


class RetiresmartzViewSet(ApiViewMixin, NestedViewSetMixin, ModelViewSet):
    model = RetirementPlan

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
    def suggested_retirement_income(self):
        """
        Calculates a suggested retirement income based on the client's retirement plan and personal profile.
        """
        # TODO: Make this work
        return Response(1234)

    @detail_route(methods=['get'], url_path='calculate-contributions')
    def calculate_contributions(self):
        """
        Calculates suggested contributions (value for the amount in the btc and atc) that will generate the desired
        retirement income.
        """
        # TODO: Make this work
        return Response({'btc_amount': 1111, 'atc_amount': 0})

    @detail_route(methods=['get'], url_path='calculate-income')
    def calculate_income(self):
        """
        Calculates retirement income possible given the current contributions and other details on the retirement plan.
        """
        # TODO: Make this work
        return Response(2345)

    @detail_route(methods=['get'], url_path='calculate-balance-income')
    def calculate_balance_income(self):
        """
        Calculates the retirement balance required to provide the desired_income as specified in the plan.
        """
        # TODO: Make this work
        return Response(5555555)

    @detail_route(methods=['get'], url_path='calculate-income-balance')
    def calculate_income_balance(self):
        """
        Calculates the retirement income possible with a supplied retirement balance and other details on the
        retirement plan.
        """
        # TODO: Make this work
        return Response(1357)

    @detail_route(methods=['get'], url_path='calculate-balance-contributions')
    def calculate_balance_contributions(self):
        """
        Calculates the retirement balance generated from the contributions.
        """
        # TODO: Make this work
        return Response(6666666)

    @detail_route(methods=['get'], url_path='calculate-contributions-balance')
    def calculate_contributions_balance(self):
        """
        Calculates the contributions required to generate the given retirement balance.
        """
        # TODO: Make this work
        return Response({'btc_amount': 2222, 'atc_amount': 88})
