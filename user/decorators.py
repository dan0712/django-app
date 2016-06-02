"""
Decorators to handle authentication (and other) wrappers for views.

- is_authenticated
- is_advisor
- is_client
- ...
"""

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def is_authenticated(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "authenticated" users only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def is_advisor(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "advisors" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_advisor,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def is_authorized_representative(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "authorized representatives" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_authorized_representative,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def is_supervisor(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "supervisors" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_supervisor,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def is_client(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that
    limit access to "clients" only
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_client,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

