from django.db.models.query_utils import Q
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response

from api.v1.permissions import IsAdvisorOrClient
from api.v1.utils import activity
from api.v1.views import ApiViewMixin

from client.models import ClientAccount
from main import constants
from main.constants import US_RETIREMENT_ACCOUNT_TYPES
from main.models import AccountType
from support.models import SupportRequest

from . import serializers


class AccountViewSet(ApiViewMixin,
                     NestedViewSetMixin,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.ReadOnlyModelViewSet):
    model = ClientAccount
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = ClientAccount.objects.all()
    pagination_class = None

    permission_classes = (IsAdvisorOrClient,)

    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = serializers.ClientAccountSerializer

    # Override this method so we can also look for accounts from signatories
    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            q = None
            try:
                for key, value in parents_query_dict.items():
                    if key == 'primary_owner':
                        tq = (Q(primary_owner=value) | Q(signatories__id=value))
                    else:
                        tq = Q({key: value})
                    if q:
                        q &= tq
                    else:
                        q = tq

                return queryset.filter(q)
            except ValueError:
                raise NotFound()
        else:
            return queryset

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializers.ClientAccountUpdateSerializer
        elif self.request.method == 'POST':
            return serializers.ClientAccountCreateSerializer
        else:
            # Default for get and other requests is the read only serializer
            return serializers.ClientAccountSerializer

    def get_queryset(self):
        """
        Because this viewset can have a primary owner and signatories,
        we don't use the queryset parsing features from NestedViewSetMixin as
        it only allows looking at one field for the parent.
        :return:
        """
        qs = super(AccountViewSet, self).get_queryset()

        # show "permissioned" records only
        user = SupportRequest.target_user(self.request)
        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)
        elif user.is_client:
            qs = qs.filter_by_client(user.client)
        else:
            raise PermissionDenied('Only Advisors or Clients '
                                   'are allowed to access goals.')

        return qs

    @detail_route(methods=['get'])
    def activity(self, request, pk=None, **kwargs):
        account = self.get_object()
        return activity.get(request, account)

    def create(self, request):
        """
        only allow one personal account per client
        """

        klass = self.get_serializer_class()
        serializer = klass(data=request.data)

        if serializer.is_valid():
            owner = serializer.validated_data['primary_owner']
            other_personals = owner.primary_accounts.filter(account_type=constants.ACCOUNT_TYPE_PERSONAL)
            if serializer.validated_data['account_type'] == constants.ACCOUNT_TYPE_PERSONAL \
                    and other_personals.count() >= 1:
                return Response({'error': 'Limit 1 personal account'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            firm = serializer.validated_data['primary_owner'].advisor.firm
            if not firm.account_types.filter(id=serializer.validated_data['account_type']).exists():
                emsg = 'Account Type: {} is not active for {}'
                a_t = AccountType.objects.filter(id=serializer.validated_data['account_type']).first()
                return Response({'error': emsg.format(a_t, firm)}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            if serializer.validated_data['account_type'] in US_RETIREMENT_ACCOUNT_TYPES:
                emsg = 'US Retirement account types are not user creatable.'
                return Response({'error': emsg}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super(AccountViewSet, self).create(request)
