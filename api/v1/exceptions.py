from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from main.models import InvalidStateError


class APIInvalidStateError(InvalidStateError, APIException):
    status_code = HTTP_400_BAD_REQUEST

    def __init__(self, current, required):
        super(APIInvalidStateError, self).__init__(current, required)

    @property
    def detail(self):
        return str(self)


class SystemConstraintError(APIException):
    status_code = HTTP_400_BAD_REQUEST
    default_detail = 'The request would have broken a system constraint.'
