from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *

from main.models import Goal, Transaction


class APITransactionsDeposit(APIView):
    def post(self, request, format=None):

        try:
            transaction = self.request.data.get('transaction', dict)

            if transaction.get('goal_id', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('goal_id'))

            if transaction.get('amount', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('amount'))

            goal_id = transaction.get('goal_id', None)

            amount = transaction.get('amount', None)

            goal = Goal.objects.get(id=goal_id)

            transaction_object = Transaction()

            transaction_object.account = goal

            transaction_object.amount = amount

            transaction_object.type = TRANSACTION_TYPE_DEPOSIT

            transaction_object.save()

            transaction_dict = {'id': transaction_object.id, 'goal_id': goal.id, 'amount': transaction_object.amount}

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'transaction': transaction_dict,
        }

        return Response(content)
