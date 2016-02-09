from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
import json


def custom_exception_handler(exc, context):
    # calling default handler to extract data.
    response = exception_handler(exc=exc, context=context)
    # this dictionary will hold api specific information.
    api = dict()

    api['version'] = 'v1'
    api['path'] = '/api/v1/'

    # Now add the HTTP status code to the response.
    if response is not None:

        api_response = dict()

        try:
            api_response = json.loads(response.data['detail'].replace('"', '\\"').replace("\'", "\""))

        except Exception as e:

            api_response['code'] = response.status_code

            if hasattr(e, 'detail'):
                api_response['detail'] = e.detail
            else:
                api_response['detail'] = response.data['detail']

            api_response['message'] = response.data['detail']

            api_response['status'] = 'error'

        response.data = {'response': api_response, 'api': api}

    return response


class ExceptionDefault(APIException):
    status_code = status.HTTP_200_OK
