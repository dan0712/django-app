# -*- coding: utf-8 -*-


def request_advisor_support(user, url, text):
    """
    Emails a given client's advisor with the
    url they had the problem on and a text message
    from the client.
    """
    if text is not None:
        user.client.advisor.user.email_user('Client Requests Support', 'Client %s at %s\n%s' % (user.client, url, text))
    else:
        user.client.advisor.user.email_user('Client Requests Support', 'Client %s at %s' % (user.client, url))
