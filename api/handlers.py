import logging

from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import exception_handler


logger = logging.getLogger('api_handler')

def api_exception_handler(exc, context):

    logger.exception("Exception in API")

    response = exception_handler(exc, context)
    print ('!!!!context', context, exc)
    error = {
        'reason': exc.__class__.__name__,
    }

    if response is None:
        error['code'] = 400

    else:
        error['code'] = response.status_code
        detail = getattr(exc, 'detail', {})

        if isinstance(exc, exceptions.ValidationError):
            non_field_errors = detail.pop('non_field_errors', [])
            non_field_errors = map(lambda s: str(s), non_field_errors) # stringify values

            error['message'] = ' '.join(non_field_errors) or 'Validation errors'

            if detail:
                error['errors'] = detail

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
