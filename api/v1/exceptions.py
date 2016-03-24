from rest_framework.exceptions import APIException
from rest_framework import status

from main.models import InvalidStateError


class APIInvalidStateError(InvalidStateError, APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, current, required):
        super(APIInvalidStateError, self).__init__(current, required)

    @property
    def detail(self):
        return str(self)