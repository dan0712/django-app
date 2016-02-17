from rest_framework import viewsets, status
from rest_framework.response import Response

from main.models import Goal
from ..views import ApiViewMixin
from ..permissions import (
    IsAdvisor,
    IsMyAdvisorCompany,
    IsAdvisorOrClient,
)

from . import serializers
#import .filters


class GoalViewSet(ApiViewMixin, viewsets.ModelViewSet):
    queryset = Goal.objects.all() \
        .select_related('account') \
        #.defer('account__data') \
    serializer_class = serializers.GoalSerializer
    permission_classes = (
        #IsAdvisorOrClient,
        #IsMyAdvisorCompany,
    )

    #filter_class = filters.GoalFilter
    #filter_fields = ('name')
    #search_fields = ('name')

    # TODO: specify permissions for Client for "write" actions

    def get_serializer_class(self):
        if self.request.method == 'GET':
            if self.action == 'list':
                return serializers.GoalListSerializer
            else:
                return serializers.GoalSerializer
        else:
            return serializers.GoalUpdateSerializer

    def get_queryset(self):
        qs = self.queryset

        # hide "slow" fields for list view
        if self.action == 'list':
            # qs = qs.defer('data')
            qs = qs.select_related()

        # show "permissioned" records only
        user = self.request.user

        if user.is_advisor:
            qs = qs.filter_by_advisor(user.advisor)

        if user.is_client:
            qs = qs.filter_by_client(user.client)

        return qs
