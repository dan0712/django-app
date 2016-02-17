from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:

        if isinstance(exc, exceptions.ValidationError):
            detail = getattr(exc, 'detail')

            non_field_errors = detail.get('non_field_errors', [])
            non_field_errors = map(lambda s: str(s), non_field_errors) # de-proxify values

            response.data['error'] = {
                'message': ' '.join(non_field_errors) or 'Uknown error',
                'errors': detail.get('field_errors'),
            }

            response.data.pop('non_field_errors', None)
            response.data.pop('field_errors', None)

        else:
            detail = response.data.pop('detail', None)

            if isinstance(detail, (tuple, list, dict)):
                response.data['error'] = {
                    'message': detail or 'Uknown error',
                    'errors': detail,
                }

            else:
                response.data['error'] = {
                    'message': detail or 'Uknown error',
                }

        # always (smile) return 200 OK status
        response.data['status'] = response.status_code
        response = Response(response.data, status=status.HTTP_200_OK)

    return response
