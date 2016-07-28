import logging

from django.conf import settings
from django.utils.timezone import now

from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import exception_handler

logger = logging.getLogger('api_exceptions')


def api_exception_handler(exc, context):

    response = exception_handler(exc, context)

    error = {
        'reason': exc.__class__.__name__,
    }

    if response is None:
        # It's not an api exception, but a bug. Log it.
        logger.exception("Uncaught Non-API exception")
        # If we're in DEBUG mode, return the full exception (Returning None makes DRF do this).
        if settings.DEBUG:
            return None
        else:
            msg = 'A Betasmartz internal error has occurred at time: {}. Please quote incident number: {}'
            error['code'] = HTTP_500_INTERNAL_SERVER_ERROR
            error['message'] = msg.format(now(), 'TODO')
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
