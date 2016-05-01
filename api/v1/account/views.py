from django.db.models.query_utils import Q
from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework_extensions.mixins import NestedViewSetMixin

from api.v1.views import ApiViewMixin

from main.models import ClientAccount

from . import serializers


class AccountViewSet(ApiViewMixin,
                     NestedViewSetMixin,
                     mixins.UpdateModelMixin,
                     viewsets.ReadOnlyModelViewSet):
    model = ClientAccount
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = ClientAccount.objects.all()
    pagination_class = None

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
        if self.request.method == 'GET':
            return serializers.ClientAccountSerializer
        elif self.request.method == 'PUT':
            return serializers.ClientAccountUpdateSerializer

    def get_queryset(self):
        """
        Because this viewset can have a primary owner and signatories, we don't use the queryset parsing features from
        NestedViewSetMixin as it only allows looking at one field for the parent.
        :return:
        """
        qs = super(AccountViewSet, self).get_queryset()

        # show "permissioned" records only
        user = self.request.user
        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)
        elif user.is_client:
            qs = qs.filter_by_client(user.client)
        else:
            raise PermissionDenied('Only Advisors or Clients are allowed to access goals.')

        return qs
