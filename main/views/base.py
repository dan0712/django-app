__author__ = 'cristian'

from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import View
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import views
from django.conf import settings

__all__ = ["AdvisorView", "ClientView", "AdminView", "LegalView"]


def advisor_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/firm/login'):

    return user_passes_test(
        lambda u: u.is_active and hasattr(u, "advisor"),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)


def legal_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/firm/login'):

    return user_passes_test(
        lambda u: u.is_active and hasattr(u, "authorised_representative"),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)


def client_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/firm/login'):

    return user_passes_test(
        lambda u: u.is_active and hasattr(u, "client"),
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
        self.firm = request.user.authorised_representative.firm
        response = super(LegalView, self).dispatch(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data["profile"] = request.user.authorised_representative
            response.context_data["firm"] = request.user.authorised_representative.firm
            response.context_data["is_legal_view"] = True
        return response


class ClientView(View):
    @method_decorator(client_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ClientView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ClientView, self).get_context_data(**kwargs)
        ctx["profile"] = self.request.user.client
        ctx["is_advisor"] = "true" if self.request.session.get("is_advisor", False) else "false"
        ctx["is_demo"] = "true" if settings.IS_DEMO else "false"
        return ctx


class AdminView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)
