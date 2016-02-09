from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *


class APIClient(APIView):
    def get(self, request, format=None):

        try:

            client = self.request.user.client

            client_data = ClientSerializer(client).data

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'client': client_data,
        }

        return Response(content)

class APIClientAccounts(APIView):
    def get(self, request, format=None):

        try:

            client = self.request.user.client

            client_data = ClientSerializer(client).data

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'client': client_data,
        }

        return Response(content)
