def response_user_registered_login_successful():
    response = dict()

    response['code'] = 'response_login_successful'

    response['status'] = 'success'

    response['message'] = 'User registered and login Successful.'

    response['detail'] = 'User registered and login Successful.'

    return response


def response_missing_fields(field=''):
    response = dict()

    response['code'] = 'response_missing_fields'

    response['status'] = 'error'

    response['message'] = 'Missing "%s" field.' % (field)

    response['detail'] = 'Missing "%s" field.' % (field)

    return response
