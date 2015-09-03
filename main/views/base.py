__author__ = 'cristian'

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import View
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import views

__all__ = ["AdvisorView", "ClientView", "AdminView", "LegalView"]


def advisor_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/firm/login'):
    """
    Decorator for views that checks that the user is logged in and is an advisor
    member, displaying the login page if necessary.
    """
    return user_passes_test(
        lambda u: u.is_active and hasattr(u, "advisor"),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)


def legal_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/firm/login'):
    """
    Decorator for views that checks that the user is logged in and is an advisor
    member, displaying the login page if necessary.
    """
    return user_passes_test(
        lambda u: u.is_active and hasattr(u, "legal_representative"),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)


def client_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='client:login'):
    """
    Decorator for views that checks that the user is logged in and is an advisor
    member, displaying the login page if necessary.
    """
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)


class AdvisorView(View):
    advisor = None

    @method_decorator(advisor_member_required)
    def dispatch(self, request, *args, **kwargs):
        self.advisor = request.user.advisor
        response = super(AdvisorView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data["profile"] = request.user.advisor
            response.context_data["firm"] = request.user.advisor.firm
            response.context_data["is_advisor_view"] = True
        return response


class LegalView(View):

    def __init__(self, *args, **kwargs):
        self.firm = None
        super(LegalView, self).__init__(*args, **kwargs)

    @method_decorator(legal_member_required)
    def dispatch(self, request, *args, **kwargs):
        self.firm = request.user.legal_representative.firm
        response = super(LegalView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data["profile"] = request.user.legal_representative
            response.context_data["firm"] = request.user.legal_representative.firm
            response.context_data["is_legal_view"] = True
        return response


class ClientView(View):
    @method_decorator(client_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ClientView, self).dispatch(request, *args, **kwargs)


class AdminView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)
