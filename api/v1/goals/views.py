from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *


class APIGoalTypes(APIView):
    def get(self, request, format=None):

        try:

            goal_types = GoalTypes.objects.filter().all()

            goal_types_data = GoalTypesSerializer(goal_types, many=True).data

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'goal_types': goal_types_data,
        }

        return Response(content)


class APIGoal(APIView):
    def post(self, request, format=None):

        try:

            user = self.request.user

            goal = self.request.data.get('goal', dict)

            if goal.get('name', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('name'))

            if goal.get('goal_type_id', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('goal_type_id'))

            if goal.get('ethical_investments', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('ethical_investments'))

            if goal.get('amount', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('amount'))

            if goal.get('duration', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('duration'))

            if goal.get('initialDeposit', None) is None:
                raise ExceptionDefault(detail=response_missing_fields('initialDeposit'))

            name = goal.get('name', None)

            goal_type_id = goal.get('goal_type_id', None)

            ethical_investments = goal.get('ethical_investments', None)

            amount = goal.get('amount', None)

            duration = goal.get('duration', None)

            initialDeposit = goal.get('initialDeposit', None)

            goal_object = Goal()

            goal_object.name = name

            goal_object.account = user.client

            goal_object.type = GoalTypes.objects.get(id=goal_type_id).name

            goal_object.ethical_investments = ethical_investments

            goal_object.amount = amount

            goal_object.duration = duration

            goal_object.initialDeposit = initialDeposit

            goal_object.save()

            goal_dict = {'id': goal_object.id, 'name': goal_object.name, 'goal_type_id': goal_object.type,
                         'ethical_investments': goal_object.ethical_investments, 'amount': goal_object.amount,
                         'duration': goal_object.duration, 'initialDeposit': goal_object.initialDeposit}

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'goal': goal_dict,
        }

        return Response(content)
