import datetime
import time
import ujson

from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Performer, PERFORMER_GROUP_STRATEGY, SymbolReturnHistory

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

            obj['id'] = p.id
            obj["group"] = p.group
            obj["initial"] = False
            obj["lineID"] = counter
            obj["returns"] = []
            returns = SymbolReturnHistory.objects.filter(
                symbol=p.symbol).order_by('date').all()
            if returns:
                b_date = returns[0].date - datetime.timedelta(days=1)
                obj["returns"].append({
                    "d": "{0}".format(int(1000 * time.mktime(b_date.timetuple(
                    )))),
                    "i": 0,
                    "ac": 1,
                    "zero_balance": True
                })
            for r in returns:
                r_obj = {
                    "d":
                        "{0}".format(int(1000 * time.mktime(r.date.timetuple()))),
                    "i": r.return_number
                }
                if p.group == PERFORMER_GROUP_STRATEGY:
                    r_obj["ac"] = p.allocation
                obj["returns"].append(r_obj)

            ret.append(obj)

        return Response(ret)
