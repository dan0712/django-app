from django.conf import settings

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):

    response = exception_handler(exc, context)

    error = {
        'reason': exc.__class__.__name__,
    }

    if response is None:
        if settings.DEBUG:
            return response # it's not an api exception (certainly the bug)
        else:
            error['code'] = 400

    else:
        error['code'] = response.status_code
        detail = getattr(exc, 'detail', {})

        if isinstance(exc, exceptions.ValidationError):
            non_field_errors = detail.pop('non_field_errors', []) if isinstance(detail, dict) else []
            non_field_errors = map(lambda s: str(s), non_field_errors) # stringify values

            error['message'] = ' '.join(non_field_errors) or 'Validation errors'

            if detail:
                error['errors'] = detail

            if isinstance(response.data, dict):
                response.data.pop('non_field_errors', None)

        else:
            if isinstance(detail, (tuple, list, dict)):
                all_errors = map(lambda s: str(s), detail) # stringify values
                error['message'] = ' '.join(all_errors) or 'Uknown error'
                error['errors'] = detail

            else:
                error['message'] = str(detail) or 'Uknown error'

    # Set an error and remove all other passed data
    response = Response({'error': error}, status=error['code'])

    return response
