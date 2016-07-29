import datetime
import time
import ujson

from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.constants import EPOCH_DT
from main.models import Performer, SymbolReturnHistory
from main.constants import PERFORMER_GROUP_STRATEGY

from ..views import ApiViewMixin


class ReturnsView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # get all the performances
        ret = []
        counter = 0
        for p in Performer.objects.all():
            counter += 1
            obj = {}
            if p.group == PERFORMER_GROUP_STRATEGY:
                obj["name"] = p.name
            else:
                obj["name"] = "{0} ({1})".format(p.name, p.symbol)

            obj["group"] = p.group
            returns = (SymbolReturnHistory
                       .objects
                       .filter(symbol=p.symbol)
                       .order_by('date')
                       .values_list('date', 'return_number')
                       )

            obj["returns"] = [((row[0] - EPOCH_DT).days, row[1]) for row in returns]
            ret.append(obj)

        return Response(ret)
