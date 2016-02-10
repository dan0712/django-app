from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.utils.api_exceptions import *
from api.v1.utils.api_responses import *
from api.v1.utils.api_serializers import *


class APIUserLevel(APIView):

    def get(self, request, format=None):
        """
        ---
        type:
          advisor:
            type: boolean
          client:
            type: boolean
        """
        try:

            # by default lets just set both false.
            client = False
            advisor = False

            user = self.request.user

            # check if they have client node
            if hasattr(user, 'client'):
                # now check if client node is not NULL
                if user.client is not None:
                    client = True

            # check if they have advisor node
            if hasattr(user, 'advisor'):
                # now check if advisor node is not NULL
                if user.advisor is not None:
                    advisor = True

        except Exception as e:

            if hasattr(e, 'detail'):

                response = e.detail

            else:
                response = dict()
                response['message'] = str(e.message)
                response['status'] = 'error'

            raise ExceptionDefault(detail=response)

        content = {
            'client': client,
            'advisor': advisor,
        }

        return Response(content)
