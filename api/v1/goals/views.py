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
